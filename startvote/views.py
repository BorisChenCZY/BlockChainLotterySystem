from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django import forms
from . import models
from .models import User
# Create your views here.
class UserForm(forms.Form):
    username = forms.CharField(label='username',max_length=50)
    password = forms.CharField(label='password',widget=forms.PasswordInput())


def hello(request):
    return HttpResponse('<html>hi </html>')

def index(request):
    articles =  models.Artivle.objects.all()
    return render(request,'index.html',{'artilces':articles})

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        userform = UserForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                return render(request, 'card.html')
            else:
                return HttpResponse('username or password is wrong!')

def form(request):
    return render(request,'form.html',)

def card(request):
    return render(request,'card.html',)

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

