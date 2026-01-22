from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 회원가입
    path('signup/', views.signup, name='signup'),
    
    # 로그인
    path('login/', views.login_view, name='login'),
    
    # 로그아웃
    path('logout/', views.logout_view, name='logout'),
    
    # 프로필 보기
    path('<str:username>/', views.profile, name='profile'),
    
    # 프로필 수정
    path('<str:username>/edit/', views.profile_edit, name='profile_edit'),
    
    # 팔로우/언팔로우
    path('<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    
    # 유저 검색
    path('search/', views.user_search, name='search'),
]