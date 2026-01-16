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


def calculate_similarity(vec1, vec2):
    if not vec1 or not vec2: return 0.0
    
    # 1. 내적(Dot Product) 계산
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # 2. 크기(Magnitude) 계산
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

# --- [챗봇 API 뷰] ---
@csrf_exempt
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_question = data.get('question', '')
        
        if not user_question:
            return JsonResponse({'error': '질문이 없습니다.'}, status=400)

        api_key = os.environ.get('UPSTAGE_API_KEY')
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # 1. 사용자의 질문을 임베딩 (query 모델 사용)
        embed_url = "https://api.upstage.ai/v1/solar/embeddings"
        embed_resp = requests.post(
            embed_url, 
            headers=headers, 
            json={
                "model": "solar-embedding-1-large-query", # 질문용 모델
                "input": user_question
            }
        )
        query_vector = embed_resp.json()['data'][0]['embedding']

        # 2. DB에서 가장 비슷한 영화 찾기 (Retrieve)
        movies = Movie.objects.exclude(embedding__isnull=True)
        scored_movies = []

        for movie in movies:
            score = calculate_similarity(query_vector, movie.embedding)
            scored_movies.append((score, movie))

        # 유사도 점수 높은 순으로 정렬 후 상위 3개만 뽑기
        scored_movies.sort(key=lambda x: x[0], reverse=True)
        top_movies = scored_movies[:3]

        # 3. LLM에게 줄 문맥(Context) 만들기
        context_text = ""
        for score, movie in top_movies:
            context_text += f"영화 제목: {movie.title}\n줄거리: {movie.overview}\n평점: {movie.vote_average}\n\n"

        # 4. Solar LLM에게 답변 요청 (Generate)
        chat_url = "https://api.upstage.ai/v1/solar/chat/completions"
        system_message = (
            "당신은 영화 추천 전문가입니다. "
            "아래 제공된 [영화 정보]를 바탕으로 사용자의 질문에 친절하게 답해주세요. "
            "정보에 없는 내용은 지어내지 말고 모른다고 하세요."
        )
        
        chat_resp = requests.post(
            chat_url,
            headers=headers,
            json={
                "model": "solar-1-mini-chat", # 채팅용 모델
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"[영화 정보]\n{context_text}\n\n사용자 질문: {user_question}"}
                ]
            }
        )
        
        bot_answer = chat_resp.json()['choices'][0]['message']['content']
        
        return JsonResponse({'answer': bot_answer})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def movie_list(request):
    # 1. 정렬 값 가져오기 (기본값: 최신순)
    sort = request.GET.get('sort', 'latest')
    # 2. 검색어 가져오기
    query = request.GET.get('q', '')

    # 기본 쿼리셋
    movies = Movie.objects.all()

    # 3. 검색 로직 (제목 기준 검색)
    if query:
        movies = movies.filter(Q(title__icontains=query))

    # 4. 정렬 로직
    if sort == 'rating':
        movies = movies.order_by('-vote_average') # 평점 높은 순
    elif sort == 'latest':
        movies = movies.order_by('-release_date') # 최신 개봉 순
    else:
        movies = movies.order_by('-created_at')   # 등록 순

    context = {
        "movies": movies,
        "query": query,
        "sort": sort,
    }
    return render(request, "reviews/movie_list.html", context)
    
def review_list(request):
    sort = request.GET.get('sort', '-release_year')

    if sort == 'release':
        reviews = Review.objects.all().order_by('-release_year') 
    elif sort == 'genre':
        reviews = Review.objects.all().order_by('genre')    
    elif sort == 'rating':
        reviews = Review.objects.all().order_by('-rating')     
    else:
        reviews = Review.objects.all().order_by('-release_year')
    
    context = {
        "reviews": reviews  
    }
    return render(request, "reviews/reviews_list.html", context) 

def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    context = {
        "review": review
    }
    return render(request, 'reviews/review_detail.html', context)


def review_create(request):
    if request.method == 'POST':
       
        Review.objects.create(
            title = request.POST.get('title'),
            director = request.POST.get('director'),
            main_actor = request.POST.get('main_actor'),
            genre = request.POST.get('genre'),
            rating = request.POST.get('rating'),
            release_year = request.POST.get('release_year'),
            runtime = request.POST.get('runtime'),
            content = request.POST.get('content'),
        )
        return redirect('reviews:review_list') 
    
  
    return render(request, 'reviews/review_create.html')


def review_update(request, pk):
    review = Review.objects.get(id=pk)
    if request.method == 'POST':
      
        review.title = request.POST.get('title')
        review.director = request.POST.get('director')
        review.main_actor = request.POST.get('main_actor')
        review.genre = request.POST.get('genre')
        review.rating = request.POST.get('rating')
        review.release_year = request.POST.get('release_year')
        review.runtime = request.POST.get('runtime')
        review.content = request.POST.get('content')
        review.save() 
        
        return redirect('reviews:review_detail', pk=review.pk)
    
    return render(request, 'reviews/review_update.html', {'review': review})


def review_delete(request, pk):
    if request.method == 'POST':
        review = Review.objects.get(id=pk)
        review.delete()
    return redirect('reviews:review_list')
    

def chat_page(request):
    return render(request, 'reviews/chat.html')