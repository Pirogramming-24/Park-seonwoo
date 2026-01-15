import re

def extract_nutrition(ocr_text: str) -> dict:
    """
    OCR 텍스트에서 영양성분 수치를 스마트하게 추출합니다.
    (g을 9로 읽는 오류 보정 + 공백 유지로 인식률 향상)
    """
    # 1. 소문자 변환만 하고, 공백은 유지합니다! (중요)
    # 공백이 있어야 "60 9"를 "609"가 아니라 "60"과 "9(g)"로 구분할 수 있습니다.
    t = ocr_text.lower().replace("\n", " ")

    # 2. 칼로리 찾기
    kcal = 0.0
    # "390 kcal", "390kcal" 모두 찾음
    m = re.search(r'([0-9]+)\s*kcal', t)
    if m:
        kcal = float(m.group(1))

    # 3. 영양성분 찾기 헬퍼 함수
    def find_g(name_list):
        for name in name_list:
            # 설명:
            # {name} 뒤에 공백(\s*)이 있고 숫자([0-9]+)가 나옴
            # 그 뒤에 단위가 나오는데, AI가 'g'를 숫자 '9'나 '6'으로 잘못 읽는 경우가 많음
            # 그래서 (g|mg|9|6)을 단위로 인정해줌!
            pattern = rf'{name}\s*([0-9]+)\s*(mg|g|9|6)'
            m = re.search(pattern, t)
            
            if m:
                val = float(m.group(1)) # 숫자 (예: 60)
                unit = m.group(2)       # 단위 (예: 9)
                
                # 단위가 mg이면 1000으로 나누고, g/9/6이면 그냥 g으로 침
                if unit == 'mg':
                    return round(val / 1000, 3)
                else:
                    return round(val, 3)
        return 0.0

    # 4. 결과 반환 (JS가 기다리는 키 이름 'kcal', 'carbohydrate' 등으로 통일)
    return {
        "calories_kcal": kcal,      # 모델 필드명과 일치!
        "carbs_g": find_g(["탄수화물", "탄수", "당질", "carb"]), # 모델 필드명과 일치!
        "protein_g": find_g(["단백질", "단백", "pro"]),
        "fat_g": find_g(["지방", "fat"]),
    }