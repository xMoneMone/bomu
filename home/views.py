from django.shortcuts import render
from posts.models import CanvasPost
from django.db.models import Count


def home(request):
    posts = CanvasPost.objects.filter().annotate(num=Count('canvaslike')).order_by('-num')
    context = {'posts': posts}
    return render(request, template_name="home.html", context=context)


def home_new(request):
    posts = CanvasPost.objects.all().order_by('-id')
    context = {'posts': posts}
    return render(request, template_name="home.html", context=context)
