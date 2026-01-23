from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Story, StoryImage
from .forms import StoryForm


# 스토리 목록 (팔로우한 사람들의 스토리)
@login_required
def story_list(request):
    # 내가 팔로우한 사람들의 스토리 + 내 스토리
    following_users = request.user.following.all()
    stories = Story.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).distinct().order_by('-created_at')
    
    context = {
        'stories': stories,
    }
    return render(request, 'stories/list.html', context)


# 스토리 생성
@login_required
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        
        if form.is_valid() and images:
            # Story 생성
            story = Story.objects.create(author=request.user)
            
            # 여러 이미지 저장
            for idx, image in enumerate(images):
                StoryImage.objects.create(
                    story=story,
                    image=image,
                    order=idx
                )
            
            return redirect('posts:list')
    else:
        form = StoryForm()
    
    context = {'form': form}
    return render(request, 'stories/form.html', context)


# 스토리 보기
@login_required
def story_view(request, pk):
    story = get_object_or_404(Story, pk=pk)
    images = story.images.all().order_by('order')
    
    # 다음/이전 스토리 찾기 (같은 작성자의)
    next_story = Story.objects.filter(
        author=story.author,
        created_at__lt=story.created_at
    ).order_by('-created_at').first()
    
    prev_story = Story.objects.filter(
        author=story.author,
        created_at__gt=story.created_at
    ).order_by('created_at').first()
    
    context = {
        'story': story,
        'images': images,
        'next_story': next_story,
        'prev_story': prev_story,
    }
    return render(request, 'stories/view.html', context)


# 스토리 삭제
@login_required
def story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    
    # 작성자만 삭제 가능
    if story.author == request.user:
        story.delete()
    
    return redirect('posts:list')