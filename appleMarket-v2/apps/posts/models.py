from django.db import models
from django.utils import timezone
from apps.users.models import User

class Post(models.Model):
    title = models.CharField('제목', max_length=20)
    content = models.CharField('내용', max_length=20)
    region = models.CharField('지역', max_length=20)
    user = models.ForeignKey(User, verbose_name='작성자', on_delete=models.CASCADE)
    price = models.IntegerField('가격', default=1000)
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', null=True, blank=True)
    photo = models.ImageField('이미지', blank=True, upload_to='posts/%Y%m%d')

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class NutritionInfo(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="nutrition")
    calories_kcal = models.FloatField('칼로리(kcal)', null=True, blank=True)
    carbs_g = models.FloatField('탄수화물(g)', null=True, blank=True)
    protein_g = models.FloatField('단백질(g)', null=True, blank=True)
    fat_g = models.FloatField('지방(g)', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)