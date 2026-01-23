from django.db import models
from django.conf import settings

class Story(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'
    
    def __str__(self):
        return f'{self.author.username}의 스토리 - {self.created_at.strftime("%Y-%m-%d")}'
    
    @property
    def images_count(self):
        return self.images.count()


class StoryImage(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='story_images/')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.story.author.username} 스토리 이미지 {self.order}'