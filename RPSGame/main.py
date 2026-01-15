import mediapipe as mp
import math, time
from mediapipe.tasks.python import vision
import cv2

import math
from visualization import draw_manual, print_RSP_result

## 필요한 함수 작성
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

def get_dist(p1, p2):
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

# Create a hand landmarker instance with the live stream mode:
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    # 1. 화면 가져오기 및 복사
    frame = output_image.numpy_view()
    annotated_image = frame.copy()
    
    # 가위바위보 결과를 저장할 변수 (초기값: None)
    rps_result = None

    # 2. 손이 감지되었을 때만 로직 실행
    if result.hand_landmarks:
        hand = result.hand_landmarks[0] # 첫 번째 손 데이터
        wrist = hand[0] # 0번: 손목 (기준점)
        
        # 안내문 가이드: 거리 계산 함수 (피타고라스 정리)
        def get_dist(p1, p2):
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

        # 3. 각 손가락이 펴졌는지 확인 (안내문 기준: TIP-손목 vs PIP-손목 거리 비교)
        # 검지(8,6), 중지(12,10), 약지(16,14), 소지(20,18)
        up_fingers = 0
        for tip_idx, pip_idx in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            dist_tip = get_dist(hand[tip_idx], wrist)
            dist_pip = get_dist(hand[pip_idx], wrist)
            
            if dist_tip > dist_pip: # 끝점 거리가 더 멀면 펴진 것
                up_fingers += 1

        # 4. 펴진 손가락 개수로 가위, 바위, 보 판별
        if up_fingers == 0:
            rps_result = 0 # Rock
        elif up_fingers == 4:
            rps_result = 1 # Paper
        elif up_fingers == 2:
            rps_result = 2 # Scissors

    # 5. 시각화: 손가락 그리고 결과 텍스트 출력
    annotated_image = draw_manual(annotated_image, result)
    annotated_image = print_RSP_result(annotated_image, rps_result) # 선우님 함수 호출

    # 6. 최종 화면 띄우기
    cv2.imshow('MediaPipe Hand Landmarks', annotated_image)
    cv2.waitKey(1)

    

if __name__ == "__main__":
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)
        
    with HandLandmarker.create_from_options(options) as landmarker:
        cap = cv2.VideoCapture(0) #
        while cap.isOpened(): #
            ret, frame = cap.read() #
            if not ret: break

            # 1. 데이터 변환 (루프 안쪽)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # 2. AI 분석 요청 (루프 안쪽)
            frame_timestamp_ms = int(time.time() * 1000)
            landmarker.detect_async(mp_image, frame_timestamp_ms)
            
            # 'q' 누르면 종료
          
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

        cap.release() #
        cv2.destroyAllWindows() #