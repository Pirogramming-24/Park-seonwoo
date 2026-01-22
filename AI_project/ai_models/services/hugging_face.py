"""
Hugging Face Transformers 로컬 서비스
모든 AI 모델을 서버에서 직접 실행
"""
from transformers import pipeline
from PIL import Image
import io
import torch

# GPU 사용 가능 여부 확인
device = 0 if torch.cuda.is_available() else -1


class HuggingFaceService:
    """Hugging Face Transformers 서비스 클래스"""
    
    # 모델 파이프라인 캐싱 (한 번만 로드)
    _image_caption_pipeline = None
    _speech_to_text_pipeline = None
    _audio_classification_pipeline = None
    _summarization_pipeline = None
    _text_generation_pipeline = None
    
    @classmethod
    def _get_image_caption_pipeline(cls):
        """이미지 캡셔닝 파이프라인 로드"""
        if cls._image_caption_pipeline is None:
            print("📥 이미지 캡셔닝 모델 로딩 중...")
            cls._image_caption_pipeline = pipeline(
                "image-to-text",
                model="Salesforce/blip-image-captioning-base",
                device=device
            )
        return cls._image_caption_pipeline
    
    @classmethod
    def _get_speech_to_text_pipeline(cls):
        """음성→텍스트 파이프라인 로드"""
        if cls._speech_to_text_pipeline is None:
            print("📥 음성 인식 모델 로딩 중...")
            cls._speech_to_text_pipeline = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-tiny",  # tiny: 빠름, small: 정확
                device=device
            )
        return cls._speech_to_text_pipeline
    
    @classmethod
    def _get_audio_classification_pipeline(cls):
        """음악 장르 분류 파이프라인 로드"""
        if cls._audio_classification_pipeline is None:
            print("📥 음악 분류 모델 로딩 중...")
            cls._audio_classification_pipeline = pipeline(
                "audio-classification",
                model="MIT/ast-finetuned-audioset-10-10-0.4593",
                device=device
            )
        return cls._audio_classification_pipeline
    
    @classmethod
    def _get_summarization_pipeline(cls):
        """텍스트 요약 파이프라인 로드"""
        if cls._summarization_pipeline is None:
            print("📥 요약 모델 로딩 중...")
            cls._summarization_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=device
            )
        return cls._summarization_pipeline
    
    @classmethod
    def _get_text_generation_pipeline(cls):
        """텍스트 생성 파이프라인 로드"""
        if cls._text_generation_pipeline is None:
            print("📥 텍스트 생성 모델 로딩 중...")
            cls._text_generation_pipeline = pipeline(
                "text-generation",
                model="gpt2",
                device=device
            )
        return cls._text_generation_pipeline
    
    @staticmethod
    def image_to_caption(image_bytes):
        """
        이미지 → 캡션 생성
        
        Args:
            image_bytes: 이미지 바이트 데이터
            
        Returns:
            dict: {'caption': str, 'success': bool, 'error': str}
        """
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # 파이프라인 실행
            pipe = HuggingFaceService._get_image_caption_pipeline()
            result = pipe(image)
            
            caption = result[0]['generated_text']
            
            return {
                'caption': caption,
                'success': True,
                'error': None
            }
                
        except Exception as e:
            return {
                'caption': None,
                'success': False,
                'error': f'오류 발생: {str(e)}'
            }
    
    @staticmethod
    def audio_to_text(audio_bytes):
        """
        음성 → 텍스트 변환
        
        Args:
            audio_bytes: 오디오 바이트 데이터
            
        Returns:
            dict: {'text': str, 'success': bool, 'error': str}
        """
        try:
            # 파이프라인 실행
            pipe = HuggingFaceService._get_speech_to_text_pipeline()
            result = pipe(audio_bytes, return_timestamps=True)
            
            text = result['text']
            
            return {
                'text': text,
                'success': True,
                'error': None
            }
                
        except Exception as e:
            return {
                'text': None,
                'success': False,
                'error': f'오류 발생: {str(e)}'
            }
    
    @staticmethod
    def classify_audio_genre(audio_bytes):
        """
        음악 장르 분류
        
        Args:
            audio_bytes: 오디오 바이트 데이터
            
        Returns:
            dict: {'genres': list, 'success': bool, 'error': str}
        """
        try:
            # 파이프라인 실행
            pipe = HuggingFaceService._get_audio_classification_pipeline()
            result = pipe(audio_bytes)
            
            # 상위 5개만 반환
            genres = result[:5]
            
            return {
                'genres': genres,
                'success': True,
                'error': None
            }
                
        except Exception as e:
            return {
                'genres': None,
                'success': False,
                'error': f'오류 발생: {str(e)}'
            }
    
    @staticmethod
    def summarize_text(text):
        """
        텍스트 요약
        
        Args:
            text: 요약할 텍스트
            
        Returns:
            dict: {'summary': str, 'success': bool, 'error': str}
        """
        try:
            # 파이프라인 실행
            pipe = HuggingFaceService._get_summarization_pipeline()
            
            # BART는 1024 토큰 제한
            if len(text.split()) > 500:
                text = ' '.join(text.split()[:500])
            
            result = pipe(
                text,
                max_length=130,
                #min_length=30,
                do_sample=False
            )
            
            summary = result[0]['summary_text']
            
            return {
                'summary': summary,
                'success': True,
                'error': None
            }
                
        except Exception as e:
            return {
                'summary': None,
                'success': False,
                'error': f'요약 오류: {str(e)}'
            }
    
    @staticmethod
    def generate_image_prompt(summary):
        """
        요약 → 이미지 프롬프트 생성
        
        Args:
            summary: 요약 텍스트
            
        Returns:
            dict: {'prompt': str, 'success': bool, 'error': str}
        """
        try:
            # 파이프라인 실행
            pipe = HuggingFaceService._get_text_generation_pipeline()
            
            input_text = f"Create a podcast cover description: {summary[:100]}\nDescription:"
            
            result = pipe(
                input_text,
                max_new_tokens=50,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=50256,
                eos_token_id=50256,
                return_full_text=False,
            )
            
            prompt = result[0]['generated_text'].strip()
            
            # 너무 짧으면 원본 요약 사용
            if len(prompt) < 10:
                prompt = f"Podcast cover art: {summary[:100]}"
            
            return {
                'prompt': prompt,
                'success': True,
                'error': None
            }
                
        except Exception as e:
            # 실패 시 원본 요약 사용
            return {
                'prompt': f"Podcast cover: {summary[:100]}",
                'success': True,
                'error': None
            }
    
    @staticmethod
    def create_podcast(audio_bytes):
        """
        팟캐스트 메이커 - 복합 파이프라인
        음성 → 텍스트 → 요약 → 프롬프트
        
        Args:
            audio_bytes: 오디오 바이트 데이터
            
        Returns:
            dict: {
                'transcript': str,
                'summary': str,
                'prompt': str,
                'success': bool,
                'error': str,
                'step': str
            }
        """
        result = {
            'transcript': None,
            'summary': None,
            'prompt': None,
            'success': False,
            'error': None,
            'step': None
        }
        
        # 1단계: 음성 → 텍스트
        print("🎤 1단계: 음성→텍스트 변환 중...")
        step1 = HuggingFaceService.audio_to_text(audio_bytes)
        if not step1['success']:
            result['error'] = step1['error']
            result['step'] = '1단계 (음성→텍스트)'
            return result
        
        result['transcript'] = step1['text']
        
        # 2단계: 텍스트 요약
        print("📝 2단계: 텍스트 요약 중...")
        step2 = HuggingFaceService.summarize_text(step1['text'])
        if not step2['success']:
            result['error'] = step2['error']
            result['step'] = '2단계 (텍스트 요약)'
            return result
        
        result['summary'] = step2['summary']
        
        # 3단계: 프롬프트 생성
        print("🎨 3단계: 이미지 프롬프트 생성 중...")
        step3 = HuggingFaceService.generate_image_prompt(step2['summary'])
        result['prompt'] = step3['prompt']
        
        result['success'] = True
        print("✅ 팟캐스트 생성 완료!")
        
        return result