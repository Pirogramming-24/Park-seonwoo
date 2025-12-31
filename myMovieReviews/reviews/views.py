from django.shortcuts import render
from .models import Review

def review_list(request):
    reviews = Review.objects.all()
    context = {
        "reviews": reviews  # html에 쓸 내용은 reviews, reviews는 실제 모델에서의 데이터
    }
    return render(request, "reviews_list.html", context) 