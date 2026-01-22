from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import base64
from .services import HuggingFaceService
from .models import AIHistory

def home(request):
    """홈페이지 - 탭 메뉴"""
    return render(request, 'ai_models/home.html')

# ============================================
# 공개 탭 (비로그인 허용)
# ============================================

def image_caption(request):
    """이미지 캡셔닝 - 공개 탭"""
    result = None
    image_url = None
    history = []
    
    # 로그인 사용자의 히스토리 가져오기
    if request.user.is_authenticated:
        history = AIHistory.objects.filter(
            user=request.user,
            model_type='image_caption'
        )[:5]  # 최근 5개
    
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        
        # AI 서비스 호출
        api_result = HuggingFaceService.image_to_caption(image_bytes)
        
        if api_result['success']:
            result = api_result['caption']
            # 이미지 미리보기용 base64 인코딩
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{image_base64}"
            
            # 로그인 사용자만 히스토리 저장
            if request.user.is_authenticated:
                AIHistory.objects.create(
                    user=request.user,
                    model_type='image_caption',
                    input_file_name=image_file.name,
                    result_text=result
                )
        else:
            messages.error(request, api_result['error'])
    
    return render(request, 'ai_models/image_caption.html', {
        'result': result,
        'image_url': image_url,
        'history': history
    })

# ============================================
# 제한 탭 (로그인 필요)
# ============================================

@login_required
def speech_to_text(request):
    """음성→텍스트 변환"""
    result = None
    
    # 히스토리 가져오기
    history = AIHistory.objects.filter(
        user=request.user,
        model_type='speech_to_text'
    )[:5]
    
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        audio_bytes = audio_file.read()
        
        # AI 서비스 호출
        api_result = HuggingFaceService.audio_to_text(audio_bytes)
        
        if api_result['success']:
            result = api_result['text']
            
            # 히스토리 저장
            AIHistory.objects.create(
                user=request.user,
                model_type='speech_to_text',
                input_file_name=audio_file.name,
                result_text=result
            )
        else:
            messages.error(request, api_result['error'])
    
    return render(request, 'ai_models/speech_to_text.html', {
        'result': result,
        'history': history
    })

@login_required
def audio_genre(request):
    """음악 장르 분류"""
    result = None
    
    # 히스토리 가져오기
    history = AIHistory.objects.filter(
        user=request.user,
        model_type='audio_genre'
    )[:5]
    
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        audio_bytes = audio_file.read()
        
        # AI 서비스 호출
        api_result = HuggingFaceService.classify_audio_genre(audio_bytes)
        
        if api_result['success']:
            result = api_result['genres']
            
            # 히스토리 저장
            AIHistory.objects.create(
                user=request.user,
                model_type='audio_genre',
                input_file_name=audio_file.name,
                result_data=result  # JSON으로 저장
            )
        else:
            messages.error(request, api_result['error'])
    
    return render(request, 'ai_models/audio_genre.html', {
        'result': result,
        'history': history
    })

# ============================================
# 챌린지: 복합 모델
# ============================================

@login_required
def podcast_maker(request):
    """팟캐스트 메이커 - 음성→텍스트→요약→프롬프트"""
    transcript = None
    summary = None
    prompt = None
    
    # 히스토리 가져오기
    history = AIHistory.objects.filter(
        user=request.user,
        model_type='podcast_maker'
    )[:5]
    
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        audio_bytes = audio_file.read()
        
        # AI 서비스 호출 (복합 파이프라인)
        api_result = HuggingFaceService.create_podcast(audio_bytes)
        
        if api_result['success']:
            transcript = api_result['transcript']
            summary = api_result['summary']
            prompt = api_result['prompt']
            
            # 히스토리 저장
            AIHistory.objects.create(
                user=request.user,
                model_type='podcast_maker',
                input_file_name=audio_file.name,
                result_text=summary,  # 요약을 메인 텍스트로
                result_data={  # 전체 결과를 JSON으로
                    'transcript': transcript,
                    'summary': summary,
                    'prompt': prompt
                }
            )
        else:
            error_msg = f"{api_result['step']} 실패: {api_result['error']}"
            messages.error(request, error_msg)
            
            # 부분 성공한 데이터라도 보여주기
            transcript = api_result.get('transcript')
            summary = api_result.get('summary')
            prompt = api_result.get('prompt')
    
    return render(request, 'ai_models/podcast_maker.html', {
        'transcript': transcript,
        'summary': summary,
        'prompt': prompt,
        'history': history
    })