from django.urls import path
from . import views  # ★ 수정: views 모듈 전체를 가져옵니다.

app_name = 'users'

urlpatterns = [
  
    path('list/', views.list, name='list'),
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    
    path('<int:pk>/', views.detail, name='detail'),
]