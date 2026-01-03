from django.shortcuts import render, redirect, get_object_or_404
from .models import Idea, DevTool, IdeaStar
from django.http import HttpResponse
def main(request):
    sort = request.GET.get('sort', '-id') 
    ideas = Idea.objects.all().order_by(sort) 
    return render(request, 'ideas/main.html', {'ideas' : ideas})

def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, 'ideas/devtool_list.html', {'devtools':devtools})

def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = devtool.ideas.all()
    return render(request, 'ideas/devtool_detail.html', {'devtool':devtool, 'ideas' : ideas })

def idea_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        content = request.POST.get('content')
        interest = request.POST.get('interest')
        devtool_id = request.POST.get('devtool')
        devtool = get_object_or_404(DevTool, pk=devtool_id)

    
        idea = Idea.objects.create(
            title=title, content=content, interest=interest,
            image=image, devtool=devtool
        )
       
        return redirect('ideas:idea_detail', pk=idea.pk) 
    
    devtools = DevTool.objects.all()
    return render(request, 'ideas/idea_create.html', {'devtools': devtools})

def interest_add(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    idea.interest += 1
    idea.save()
    return HttpResponse(idea.interest)

def interest_sub(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if idea.interest > 0:
        idea.interest -= 1
        idea.save()
    return HttpResponse(idea.interest)

def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    is_starred = False
    if request.user.is_authenticated:
        if idea.ideastar_set.filter(user=request.user).exists():
            is_starred = True

    return render(request, 'ideas/idea_detail.html', {
        'idea': idea,
        'is_starred': is_starred, 
    })

def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == 'POST':
        idea.title = request.POST.get('title')
        idea.content = request.POST.get('content')
        idea.interest = request.POST.get('interest')
        if request.FILES.get('image'):
            idea.image = request.FILES.get('image')
            
        devtool_id = request.POST.get('devtool')
        idea.devtool = get_object_or_404(DevTool, pk=devtool_id)
        
        idea.save()
        return redirect('ideas:idea_detail', pk=pk)

    devtools = DevTool.objects.all()
    return render(request, 'ideas/idea_update.html', {'idea': idea, 'devtools': devtools})

def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    idea.delete()
    return redirect('ideas:main')


def devtool_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        kind = request.POST.get('kind')
        content = request.POST.get('content')
        
       
        devtool = DevTool.objects.create(name=name, kind=kind, content=content)
       
        return redirect('ideas:devtool_detail', pk=devtool.pk) 
    
    return render(request, 'ideas/devtool_create.html')

def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == 'POST':
        devtool.name = request.POST.get('name')
        devtool.kind = request.POST.get('kind')
        devtool.content = request.POST.get('content')
        devtool.save()
        return redirect('ideas:devtool_detail', pk=pk)
    return render(request, 'ideas/devtool_update.html', {'devtool': devtool})

def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    devtool.delete()
    return redirect('ideas:devtool_list')

def idea_star_toggle(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    star, created = IdeaStar.objects.get_or_create(idea=idea, user=request.user)
    
    if not created:
        star.delete()

    return redirect(request.META.get('HTTP_REFERER', 'ideas:main'))