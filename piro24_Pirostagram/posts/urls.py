from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # 게시글 목록 (피드)
    path('', views.post_list, name='list'),
    
    # 게시글 작성
    path('create/', views.post_create, name='create'),
    
    # 게시글 상세
    path('<int:pk>/', views.post_detail, name='detail'),
    
    # 게시글 수정
    path('<int:pk>/update/', views.post_update, name='update'),
    
    # 게시글 삭제
    path('<int:pk>/delete/', views.post_delete, name='delete'),
    
    # 좋아요 토글
    path('<int:pk>/like/', views.post_like, name='like'),
    
    # 댓글 작성
    path('<int:pk>/comment/', views.comment_create, name='comment_create'),
    
    # 댓글 삭제
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # 댓글 수정
    path('comment/<int:pk>/update/', views.comment_update, name='comment_update'),
]