import os
import json
import requests
import math
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q 
from .models import Review, Movie

# --- [1. 유틸리티 함수: 코사인 유사도 계산] ---
def calculate_similarity(vec1, vec2):
    if not vec1 or not vec2: return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    return dot_product / (magnitude1 * magnitude2)

# --- [2. 챗봇 API (RAG 로직)] ---
@csrf_exempt
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_question = data.get('question', '')
        if not user_question: return JsonResponse({'error': '질문이 없습니다.'}, status=400)

        api_key = os.environ.get('UPSTAGE_API_KEY')
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # (1) 질문 임베딩
        embed_resp = requests.post("https://api.upstage.ai/v1/solar/embeddings", headers=headers, json={"model": "solar-embedding-1-large-query", "input": user_question})
        query_vector = embed_resp.json()['data'][0]['embedding']

        # (2) 유사도 검색
        movies = Movie.objects.exclude(embedding__isnull=True)
        scored_movies = []
        for movie in movies:
            score = calculate_similarity(query_vector, movie.embedding)
            scored_movies.append((score, movie))
        scored_movies.sort(key=lambda x: x[0], reverse=True)
        top_movies = scored_movies[:3]

        # (3) 답변 생성
        context_text = ""
        for score, movie in top_movies:
            context_text += f"제목: {movie.title}\n줄거리: {movie.overview}\n평점: {movie.vote_average}\n\n"

        system_message = "당신은 영화 추천 전문가입니다. 제공된 정보를 바탕으로 친절하게 답해주세요."
        chat_resp = requests.post("https://api.upstage.ai/v1/solar/chat/completions", headers=headers, json={
            "model": "solar-1-mini-chat",
            "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": f"[정보]\n{context_text}\n\n질문: {user_question}"}]
        })
        return JsonResponse({'answer': chat_resp.json()['choices'][0]['message']['content']})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- [3. 메인 페이지 (통합 리스트)] ---
def main_page(request):
    tmdb_count = Movie.objects.all().count()
    review_count = Review.objects.all().count()
    total_count = tmdb_count + review_count

    movies = Movie.objects.all()
    reviews = Review.objects.all()

    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')  # 추가
    
    # 필터링 로직
    if filter_type == 'tmdb':
        reviews = Review.objects.none()
    elif filter_type == 'review':
        movies = Movie.objects.none()
    
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(overview__icontains=query))
        reviews = reviews.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(director__icontains=query) | Q(main_actor__icontains=query))

    combined_list = []
    for m in movies:
        combined_list.append({
            'type': 'TMDB', 
            'id': m.id, 
            'title': m.title, 
            'image': m.poster_path, 
            'rating': m.vote_average, 
            'year': m.release_date.year if m.release_date else '', 
            'director': 'TMDB', 
            'obj': m
        })
    for r in reviews:
        combined_list.append({
            'type': 'REVIEW', 
            'id': r.id, 
            'title': r.title, 
            'image': r.image.url if r.image else '',
            'rating': r.rating, 
            'year': r.release_year, 
            'director': r.director, 
            'obj': r
        })

    sort = request.GET.get('sort', 'latest')
    if sort == 'rating': 
        combined_list.sort(key=lambda x: float(x['rating'] or 0), reverse=True)
    elif sort == 'title': 
        combined_list.sort(key=lambda x: x['title'])
    else: 
        combined_list.reverse()

    # context에 filter_type 추가 
    return render(request, 'reviews/main.html', {
        'combined_list': combined_list, 
        'total_count': total_count, 
        'tmdb_count': tmdb_count,
        'review_count': review_count,
        'query': query, 
        'sort': sort,
        'filter': filter_type,  # 추가!
    })
# --- [4. 리뷰 CRUD (생략 없이 전부 포함)] ---
def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    return render(request, 'reviews/review_detail.html', {"review": review})

def review_create(request):
    if request.method == 'POST':
        # 숫자 처리 로직
        rating = request.POST.get('rating') or 0.0
        release_year = request.POST.get('release_year') or 0
        runtime = request.POST.get('runtime') or 0

        Review.objects.create(
            title = request.POST.get('title', ''),
            director = request.POST.get('director', ''),
            main_actor = request.POST.get('main_actor', ''),
            genre = request.POST.get('genre', 'action'),
            rating = rating,
            release_year = release_year,
            runtime = runtime,
            content = request.POST.get('content', ''),
            
            # 이미지받기
            image = request.FILES.get('image') 
        )
        return redirect('reviews:main_page') 
    
    return render(request, 'reviews/review_create.html')

def review_update(request, pk):
    review = Review.objects.get(id=pk)
    if request.method == 'POST':
        review.title = request.POST.get('title')
        review.director = request.POST.get('director')
        review.main_actor = request.POST.get('main_actor')
        review.genre = request.POST.get('genre')
        review.rating = request.POST.get('rating') or 0.0
        review.release_year = request.POST.get('release_year') or 0
        review.runtime = request.POST.get('runtime') or 0
        review.content = request.POST.get('content')
        
        # 새 이미지가 들어왔을 때만 교체
        if 'image' in request.FILES:
            review.image = request.FILES['image']
            
        review.save() 
        return redirect('reviews:review_detail', pk=review.pk)
    
    return render(request, 'reviews/review_update.html', {'review': review})

def review_delete(request, pk):
    if request.method == 'POST':
        review = Review.objects.get(id=pk)
        review.delete()
    # 삭제하면 메인 페이지로 이동
    return redirect('reviews:main_page')

# --- [5. 기타 페이지] ---
def chat_page(request):
    return render(request, 'reviews/chat.html')

# reviews/views.py

def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)
    # 장르 처리 로직 삭제 (DB에 없으므로)
    
    context = {
        'movie': movie,
    }
    return render(request, 'reviews/movie_detail.html', context)