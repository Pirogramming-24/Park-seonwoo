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

    # [중요] 검색 기능은 프로필보다 무조건 위에 있어야 합니다!
    # (그래야 'search'라는 단어를 유저 아이디로 착각하지 않습니다)
    path('search/', views.user_search, name='search'),

    # ==========================================
    # 변수(<str:username>)를 쓰는 패턴은 항상 맨 아래에 두세요.
    # ==========================================
    
    # 프로필 보기
    path('<str:username>/', views.profile, name='profile'),
    
    # 프로필 수정
    path('<str:username>/edit/', views.profile_edit, name='profile_edit'),
    
    # 팔로우/언팔로우
    path('<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
]