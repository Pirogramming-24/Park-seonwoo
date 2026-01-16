from django.urls import path 
from . import views

app_name = "reviews"

urlpatterns = [
	    path('', views.review_list, name="review_list"),
        path('<int:pk>/', views.review_detail, name='review_detail'),
        path('create/', views.review_create, name='review_create'),
        path('<int:pk>/update/', views.review_update, name='review_update'),
        path('<int:pk>/delete/', views.review_delete, name='review_delete'),
        path('movies/', views.movie_list, name='movie_list'), # 영화 검색/목록 페이지
        path('api/chat/', views.chat_api, name='chat_api'), # 챗봇 API 주소 추가
        path('chat/', views.chat_page, name='chat_page'), #채팅 페이지 접속 주소 (화면)

]

