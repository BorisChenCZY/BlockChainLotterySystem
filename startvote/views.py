from django.shortcuts import render
from django.http import  HttpResponse
from . import models

# Create your views here.

def hello(request):
    return HttpResponse('<html>hi </html>')

def index(request):
    articles =  models.Artivle.objects.all()
    return render(request,'index.html',{'artilces':articles})

def login(request):
    return render(request,'login.html',)

def form(request):
    return render(request,'form.html',)

def article_page(request,id):
    article = models.Artivle.objects.get(pk=id)
    return  render(request,'startvote/page.html',{'article':article})

def edit_page(request,id):
    if str(id)=='0':
        return render(request,'startvote/edit.html')
    article = models.Artivle.objects.get(pk=id)
    return render(request, 'startvote/edit.html',{'article':article})

def edit_action(request):
    title = request.POST.get('title','TITLE')#后面是默认值
    content = request.POST.get('content','CONTENT')
    id = request.POST.get('id','0')
    if id=='0':
        models.Artivle.objects.create(title=title,content=content)

    else:
        article =models.Artivle.objects.get(pk=id)
        article.title=title
        article.content=content
        article.save()

    articles = models.Artivle.objects.all()
    return render(request, 'startvote/index.html', {'artilces': articles})

