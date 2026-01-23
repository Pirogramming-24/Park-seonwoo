from django.urls import path
from . import views

app_name = 'ai_models'

urlpatterns = [
    path('', views.home, name='home'),
    path('image-caption/', views.image_caption, name='image_caption'),  # 공개 탭
    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),  # 로그인 필요
    path('audio-genre/', views.audio_genre, name='audio_genre'),  # 로그인 필요
    path('podcast-maker/', views.podcast_maker, name='podcast_maker'),  # 챌린지
]