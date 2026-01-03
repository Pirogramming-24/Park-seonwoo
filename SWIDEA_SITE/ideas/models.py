from django.db import models
from django.contrib.auth.models import User

class DevTool(models.Model):
    name = models.CharField(max_length=32)
    kind = models.CharField(max_length=32)
    content = models.TextField()
    def __str__(self):
        return self.name

class Idea(models.Model):
    title = models.CharField(max_length=32)
    image = models.ImageField(default='default.jpg',upload_to='ideas/')
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey(DevTool, on_delete=models.CASCADE, related_name='ideas')
    def __str__(self):
        return self.title

class IdeaStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username} - {self.idea.title} 찜"