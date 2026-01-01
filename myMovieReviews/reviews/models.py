from django.db import models

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

    def get_runtime_display(self):
        hours = self.runtime // 60  
        minutes = self.runtime % 60
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        return f"{minutes}분"
    
    def __str__(self):
        return self.title