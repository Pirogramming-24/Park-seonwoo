from django.shortcuts import render, redirect
from .models import Review

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
    return render(request, "reviews_list.html", context) 

def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    context = {
        "review": review
    }
    return render(request, 'review_detail.html', context)


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
    
  
    return render(request, 'review_create.html')


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
    
    return render(request, 'review_update.html', {'review': review})


def review_delete(request, pk):
    if request.method == 'POST':
        review = Review.objects.get(id=pk)
        review.delete()
    return redirect('reviews:review_list')
    