from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Comment
from .forms import PostForm, CommentForm


# 게시글 목록
@login_required
def post_list(request):
    from stories.models import Story
    
    # 기본: 내가 팔로우한 사람 + 내 게시글
    following_users = request.user.following.all()
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    )
    
    # 검색 기능 구현
    query = request.GET.get('q')
    if query:
        # 내용(content)에 검색어가 포함되어 있거나, 작성자 이름에 포함된 경우
        posts = posts.filter(
            Q(content__icontains=query) | 
            Q(author__username__icontains=query)
        )
    
    # 정렬 (최신순) & 중복 제거
    posts = posts.distinct().order_by('-created_at')
    
    # 스토리 로직
    stories = Story.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).distinct().order_by('-created_at')
    
    context = {
        'posts': posts,
        'stories': stories,
        'query': query, # 검색어를 템플릿에도 전달 (검색창에 유지하려고)
    }
    return render(request, 'posts/list.html', context)


# 게시글 상세
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/detail.html', context)


# 게시글 작성
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:list')
    else:
        form = PostForm()
    
    context = {'form': form}
    return render(request, 'posts/form.html', context)


# 게시글 수정
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 작성자만 수정 가능
    if post.author != request.user:
        return redirect('posts:detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', pk=pk)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'is_update': True
    }
    return render(request, 'posts/form.html', context)


# 게시글 삭제
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 작성자만 삭제 가능
    if post.author == request.user:
        post.delete()
    
    return redirect('posts:list')


# 좋아요 토글
@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 이미 좋아요를 눌렀다면 취소, 아니면 추가
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    # JSON 응답 (Ajax용)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count
        })
    
    # 일반 요청은 이전 페이지로
    return redirect(request.META.get('HTTP_REFERER', 'posts:list'))


# 댓글 작성
@login_required
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    
    return redirect('posts:detail', pk=pk)


# 댓글 수정
@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # 작성자만 수정 가능
    if comment.author != request.user:
        return redirect('posts:detail', pk=comment.post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
    
    return redirect('posts:detail', pk=comment.post.pk)


# 댓글 삭제
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    # 작성자만 삭제 가능
    if comment.author == request.user:
        comment.delete()
    
    return redirect('posts:detail', pk=post_pk)