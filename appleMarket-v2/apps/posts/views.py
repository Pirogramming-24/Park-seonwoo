from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from .models import Post
from .services.ocr_service import extract_nutrition_data
from .forms import PostForm, NutritionForm

def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'posts/list.html', context=context)

# apps/posts/views.py

def create(request):
    if request.method == 'GET':
        post_form = PostForm()         # 이름 변경: form -> post_form
        nutrition_form = NutritionForm()
        
        context = { 
            'post_form': post_form,    # ★ HTML에서 이 이름으로 씁니다!
            'nutrition_form': nutrition_form 
        }
        return render(request, 'posts/create.html', context=context)
    
    else:
        post_form = PostForm(request.POST, request.FILES) # 여기도 post_form
        nutrition_form = NutritionForm(request.POST)

        if post_form.is_valid() and nutrition_form.is_valid():
            post = post_form.save(commit=False)
            post.save()

            nutrition = nutrition_form.save(commit=False)
            nutrition.post = post
            nutrition.save()
            return redirect('/')
        
        # 실패 시 다시 입력창으로
        context = { 'post_form': post_form, 'nutrition_form': nutrition_form }
        return render(request, 'posts/create.html', context=context)
        
def detail(request, pk):
    target_post = Post.objects.get(id=pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form, 
            'post': post
        }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:detail', pk=pk)

def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

@csrf_exempt
def ocr_api(request):
    """영양성분표 OCR API (OpenCV 제거 및 최적화 버전)"""
    # 1. HTML에서 보낸 이름('nutrition_image') 확인
    if request.method == 'POST' and request.FILES.get('nutrition_image'):
        nutrition_image = request.FILES['nutrition_image']
        
        # 2. 임시 파일로 저장 (파일명 충돌 방지를 위해 시간값 추가)
        import time
        file_extension = nutrition_image.name.split('.')[-1]
        temp_filename = f'temp_ocr_{int(time.time())}.{file_extension}'
        
        path = default_storage.save(temp_filename, nutrition_image)
        full_path = default_storage.path(path)
        
        try:
            # 3. OCR 실행 (ocr_service.py 호출)
            data = extract_nutrition_data(full_path)
            
            # 4. 분석 끝났으니 임시 파일 삭제
            if default_storage.exists(path):
                default_storage.delete(path)
            
            # 5. 성공 결과 반환 (JS가 기다리는 포맷)
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            # 에러 발생 시에도 임시 파일은 지워줌
            if default_storage.exists(path):
                default_storage.delete(path)
            
            print(f"OCR Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': '유효하지 않은 요청입니다.'
    }, status=400)