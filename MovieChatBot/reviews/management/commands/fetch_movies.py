import requests
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import Movie  # 우리가 models.py에 만든 그 모델

class Command(BaseCommand):
    help = 'TMDB API를 사용하여 인기 영화 데이터를 DB에 저장합니다.'

    def handle(self, *args, **options):
        # 1. .env 또는 settings에 저장된 API 키 가져오기
        # 직접 문자열로 넣어도 되지만 보안상 settings.TMDB_API_KEY 권장
        api_key = getattr(settings, 'TMDB_API_KEY', '여기에_직접_키를_넣어도_됨')
        
        if not api_key or api_key == '여기에_직접_키를_넣어도_됨':
            self.stdout.write(self.style.ERROR('TMDB API 키가 설정되지 않았습니다.'))
            return

        # 2. TMDB 인기 영화 API 주소 (한국어 설정)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR&page=1"

        try:
            response = requests.get(url)
            data = response.json()

            # 3. 받아온 데이터 반복문 돌리며 저장
            for item in data.get('results', []):
                # update_or_create: tmdb_id가 이미 있으면 업데이트, 없으면 새로 생성
                movie, created = Movie.objects.update_or_create(
                    tmdb_id=item['id'],
                    defaults={
                        'title': item['title'],
                        'overview': item['overview'],
                        'poster_path': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
                        'release_date': item['release_date'] if item['release_date'] else None,
                        'vote_average': item['vote_average'],
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"새 영화 추가됨: {movie.title}"))
                else:
                    self.stdout.write(f"기존 영화 업데이트: {movie.title}")

            self.stdout.write(self.style.SUCCESS('성공적으로 데이터를 가져왔습니다!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'에러 발생: {e}'))