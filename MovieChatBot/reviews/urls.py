from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # 1. 메인 페이지 (통합 리스트)
    path('', views.main_page, name='main_page'),

    # 2. 리뷰 CRUD (기존 기능)
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('create/', views.review_create, name='review_create'),
    path('<int:pk>/update/', views.review_update, name='review_update'),
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),

    # 3. 챗봇 기능
    path('api/chat/', views.chat_api, name='chat_api'),
    path('chat/', views.chat_page, name='chat_page'),

    # 디테일
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
]