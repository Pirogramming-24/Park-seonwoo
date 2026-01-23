from django.db import models
from django.contrib.auth.models import User

class AIHistory(models.Model):
    """AI 모델 사용 내역"""
    
    MODEL_CHOICES = [
        ('image_caption', '이미지 캡셔닝'),
        ('speech_to_text', '음성→텍스트'),
        ('audio_genre', '음악 장르 분류'),
        ('podcast_maker', '팟캐스트 메이커'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_histories')
    model_type = models.CharField(max_length=50, choices=MODEL_CHOICES)
    
    # 입력 정보
    input_file_name = models.CharField(max_length=255, null=True, blank=True)
    
    # 출력 결과
    result_text = models.TextField(null=True, blank=True)  # 텍스트 결과
    result_data = models.JSONField(null=True, blank=True)  # JSON 결과 (장르 분류 등)
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI 사용 내역'
        verbose_name_plural = 'AI 사용 내역들'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_model_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"