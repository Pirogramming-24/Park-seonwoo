from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    # 스토리 목록
    path('', views.story_list, name='list'),
    
    # 스토리 생성
    path('create/', views.story_create, name='create'),
    
    # 스토리 보기
    path('<int:pk>/', views.story_view, name='view'),
    
    # 스토리 삭제
    path('<int:pk>/delete/', views.story_delete, name='delete'),
]