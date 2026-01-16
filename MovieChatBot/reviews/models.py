from django.db import models

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # TMDB의 고유 번호 (중복 방지)
    title = models.CharField(max_length=200)    # 영화 제목
    overview = models.TextField(blank=True)     # 영화 줄거리 (RAG 핵심 데이터)
    poster_path = models.CharField(max_length=200, null=True, blank=True) # 포스터 경로
    release_date = models.DateField(null=True, blank=True) # 개봉일
    vote_average = models.FloatField(default=0)  # 평점
    created_at = models.DateTimeField(auto_now_add=True)


    embedding = models.JSONField(null=True, blank=True) # 기능4
    def __str__(self):
        return self.title

class Review(models.Model):
    
    GENRE_CHOICES = [
        ('action', '액션'),
        ('romance', '로맨스'),
        ('comedy', '코미디'),
        ('sf', 'SF'),
        ('horror', '공포'),
    ]

    
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=32)
    main_actor = models.CharField(max_length=32)
    
    genre = models.CharField(max_length=32, choices=GENRE_CHOICES) 
    rating = models.FloatField()
    release_year = models.IntegerField()
    runtime = models.IntegerField()
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    # [추가] 이 리뷰가 TMDB의 어떤 영화와 관련 있는지 연결하는 고리
    # 기존 데이터들을 위해 null=True, blank=True를 설정합니다. (기존 데이터 안 깨짐!)
    tmdb_id = models.IntegerField(null=True, blank=True)

    def get_runtime_display(self):
        hours = self.runtime // 60  
        minutes = self.runtime % 60
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        return f"{minutes}분"
    
    def __str__(self):
        return self.title

