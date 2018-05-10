from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django import forms
from . import models
from .models import User,Vote
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
                return HttpResponseRedirect('/card')
            else:
                return render(request, "login.html", {"msg": u"用户名或密码错误"})

def form(request):
    return render(request,'form.html')

def vote(request):
    return render(request, 'vote.html')

def card(request):
    #
    # votes = Vote.objects.get(id = )   #获取数据库内容
    vote1 ={'vote_name':"2018十佳毕业生",
            'vote_description':'2018年“十佳毕业生”候选人有16位，16进10的校级评选中，他们将通过师生投票和评委评议的方式决出。师生投票在校级评选中占比为20%。',
            'state':'Unfinished'}
    vote2 = {'vote_name': "学生食堂人气投票",
             'vote_description': '荔园餐厅？湖畔餐厅？欣园食堂？',
             'state': 'Finished'}
    vote3 = {'vote_name': "周末聚餐时间",
             'vote_description': '这个周末去哪里吃？',
             'state': 'Unfinished'}
    votes = [vote1, vote2, vote3]
    print("here!")
    return render_to_response('card.html',{"votes":votes})

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

