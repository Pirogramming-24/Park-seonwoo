from django import forms
from .models import Post, NutritionInfo

class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        exclude = ['created_at', 'updated_at']

class NutritionForm(forms.ModelForm):
    class Meta:
        model = NutritionInfo
      
        exclude = ['post', 'created_at', 'updated_at']