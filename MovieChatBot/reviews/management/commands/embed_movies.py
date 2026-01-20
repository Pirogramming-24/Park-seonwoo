import os
import requests
from django.core.management.base import BaseCommand
from reviews.models import Movie

class Command(BaseCommand):
    help = '영화 줄거리를 Upstage API를 통해 임베딩(숫자화)합니다.'

    def handle(self, *args, **options):
        # 1. API 키 확인
        api_key = os.environ.get('UPSTAGE_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR(
                "❌ 에러: UPSTAGE_API_KEY가 설정되지 않았습니다."
            ))
            return

        url = "https://api.upstage.ai/v1/solar/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"  # 헤더 추가 권장
        }

        # 2. 임베딩이 필요한 영화 선택
        movies = Movie.objects.filter(
            embedding__isnull=True
        ).exclude(overview="")

        if not movies.exists():
            self.stdout.write(self.style.SUCCESS(
                "✅ 임베딩할 새로운 영화가 없습니다."
            ))
            return

        success_count = 0
        error_count = 0

        for movie in movies:
            try:
                # 3. API 요청 (정확한 모델명 사용)
                response = requests.post(
                    url, 
                    headers=headers, 
                    json={
                        "model": "solar-embedding-1-large-passage",  # 수정!
                        "input": movie.overview
                    },
                    timeout=30  # 타임아웃 추가
                )
                
                # 4. 응답 확인
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(
                        f"❌ API 에러 ({movie.title}): "
                        f"Status {response.status_code} - {response.text}"
                    ))
                    error_count += 1
                    continue
                
                result = response.json()

                # 5. 임베딩 데이터 추출 및 저장
                if 'data' in result and len(result['data']) > 0:
                    movie.embedding = result['data'][0]['embedding']
                    movie.save()
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ 임베딩 완료: {movie.title}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ 데이터 없음 ({movie.title}): {result}"
                    ))
                    error_count += 1
            
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(
                    f"❌ 네트워크 오류 ({movie.title}): {e}"
                ))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"❌ 시스템 오류 ({movie.title}): {e}"
                ))
                error_count += 1

        # 6. 최종 결과 출력
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*50}\n"
            f"처리 완료: 성공 {success_count}건, 실패 {error_count}건\n"
            f"{'='*50}"
        ))