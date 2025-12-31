from django.shortcuts import render
from .models import DinnerRecord
import random


# Create your views here.
def meals_index(request):
    menus = {
        "korean": ["비빔밥", "김치찌개", "불고기", "제육볶음"],
        "chinese": ["짜장면", "짬뽕", "탕수육", "마라탕"],
        "japanese": ["초밥", "돈카츠", "라멘", "우동"],
        "western": ["파스타", "피자", "스테이크", "햄버거"]
    }
     # GET으로 받은 값
    category = request.GET.get('category')
    result = None

    # 선택한 카테고리에 맞게 랜덤 추천
    if category in menus:
        result = random.choice(menus[category])
        DinnerRecord.objects.create(category=category, menu=result)
    elif category == "any":
        all_items = sum(menus.values(),[])
        result = random.choice(all_items)
        DinnerRecord.objects.create(category="아무거나", menu=result)
    
    records = DinnerRecord.objects.all().order_by('-id')[:2]


    # 템플릿에 전달
    return render(request, "meals_index.html", {
        'result' : result,
        'records' : records,
        'category' : category
    })
