import cv2
import numpy as np
from paddleocr import PaddleOCR
from apps.posts.services.rules import extract_nutrition

def extract_nutrition_data(image_path):
    print(f"📸 이미지 분석 시작: {image_path}")
    
    try:
        # 1. 파일 읽기
        with open(image_path, 'rb') as f:
            file_bytes = f.read()
            
        # 2. 이미지 변환
        arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        # 3. PaddleOCR 초기화 (구버전 호환)
        # 구버전은 lang='korean' 만 있어도 잘 됩니다.
        ocr = PaddleOCR(lang='korean', use_angle_cls=False, show_log=False)
        
        # 4. OCR 실행
        # ★ 구버전(2.7)에서는 cls=False가 필수이거나 권장됩니다.
        result = ocr.ocr(img, cls=False)
        
        # 5. 텍스트 합치기
        full_text = ""
        if result and result[0]:
            for line in result[0]:
                full_text += line[1][0] + " "
        
        print(f"=== 🔍 AI가 읽은 텍스트 ===\n{full_text}\n==========================")

        return extract_nutrition(full_text)

    except Exception as e:
        print(f"❌ 분석 중 에러 발생: {e}")
        return {'kcal': 0, 'carbohydrate': 0, 'protein': 0, 'fat': 0}