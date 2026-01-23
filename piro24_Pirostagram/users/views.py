from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from .forms import SignUpForm, ProfileEditForm


# 회원가입
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('posts:list')
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'users/signup.html', context)


# 로그인
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'posts:list')
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'users/login.html')


# 로그아웃
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('users:login')


# 프로필 보기
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().order_by('-created_at')
    
    # 팔로우 여부 확인
    is_following = request.user.following.filter(pk=user.pk).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
        'is_own_profile': request.user == user,
    }
    return render(request, 'users/profile.html', context)


# 프로필 수정
@login_required
def profile_edit(request, username):
    user = get_object_or_404(User, username=username)
    
    # 본인만 수정 가능
    if user != request.user:
        return redirect('users:profile', username=username)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('users:profile', username=username)
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'form': form,
        'profile_user': user
    }
    return render(request, 'users/profile_edit.html', context)


# 팔로우/언팔로우 토글
@login_required
def follow_toggle(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    # 자기 자신은 팔로우 불가
    if user_to_follow == request.user:
        return redirect('users:profile', username=username)
    
    # 이미 팔로우 중이면 언팔로우, 아니면 팔로우
    if request.user.following.filter(pk=user_to_follow.pk).exists():
        request.user.following.remove(user_to_follow)
        messages.success(request, f'{user_to_follow.username}님을 언팔로우했습니다.')
    else:
        request.user.following.add(user_to_follow)
        messages.success(request, f'{user_to_follow.username}님을 팔로우했습니다.')
    
    return redirect('users:profile', username=username)


# 유저 검색
@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        # 아이디 또는 이름으로 검색
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(pk=request.user.pk)  # 자기 자신 제외
    
    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'users/search.html', context)