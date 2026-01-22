# 파이썬 3.13 버전 사용
FROM python:3.13-slim

# 컨테이너 내 작업 폴더 설정
WORKDIR /app

# 파이썬 환경 변수 설정 (버퍼링 비활성화 등)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 패키지 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 모든 파일 복사
COPY . .

# 장고 서버 포트 8000번 개방
EXPOSE 8000

# 서버 실행 명령 (0.0.0.0은 외부 접속 허용을 위해 필수)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]