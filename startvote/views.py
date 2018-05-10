from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django import forms
from django.contrib import sessions
from . import models
from .models import User,Vote,Entry
from block import block_hashfunc
import datetime
# Create your views here.
class UserForm(forms.Form):
    username = forms.CharField(label='username',max_length=50)
    password = forms.CharField(label='password',widget=forms.PasswordInput())

# class VoteForm(forms.Form):
#     vote_name = forms.CharField(max_length=50)
#     vote_description = forms.
#     vote_type = models.IntegerField()  # 多选,单选
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     option_size = models.IntegerField()  # 选项数目
#     option_content = models.TextField()  # 选项内容,可能为一个json文件



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
                request.session['user_id'] = user.first().user_id
                return HttpResponseRedirect('/card')
            else:
                return render(request, "login.html", {"msg": u"用户名或密码错误"})

def form(request):
    if request.method == 'GET':
        return render(request, 'form.html')
    else:
        vote = Vote()
        vote.creat_time = datetime.datetime.now()
        vote.vote_name = request.POST.get("vote_name")
        vote.vote_description = request.POST.get("vote_description")
        vote.start_time = request.POST.get("start_time")
        vote.end_time = request.POST.get("end_time")

        vote.vote_state = 1  # 默认是进行中，实际通过时间计算，need more coding

        if request.POST.get("is_opened") == "yes": # 是否是公开投票
            vote.is_opened = True
        else:
            vote.is_opened = False
        if request.POST.get("is_checkable") == "须权限认证":  # 是否展示投票结果给参与者
            vote.is_checkable = True
        else:
            vote.is_checkable = False

        if request.POST.get("vote_type") == "单选":
            vote.vote_type = 1
        else:
            vote.vote_type = 2

        vote.vote_target =block_hashfunc.hash(str(vote.vote_name).encode())

        vote.save()
    # forms.cleaned_data(result)
    #     print(str(result))
        return render(request, 'card.html')
    # request.POST.



def vote(request):
    candidate = []
    candidate.append({"id":1, "option": "A. Boris.Chen","img": "/static/img/team/member1.jpg", "content": "大家好我是鲍里斯陈，来自db group，我爱麻辣火锅，谢谢大家支持。\n"*4})
    candidate.append({"id":2, "option": "B. Mark.Zeng","img": "/static/img/team/member5.jpg","content": "大家好我是马克曾，来自db group，我爱牛肉火锅，谢谢大家支持。\n"*4})
    candidate.append({"id":3, "option": "B. Mark.Zeng","img": "/static/img/team/member5.jpg","content": "大家好我是马克曾，来自db group，我爱牛肉火锅，谢谢大家支持。\n"*4})
    candidate.append({"id":4, "option": "B. Mark.Zeng","img": "/static/img/team/member5.jpg","content": "大家好我是马克曾，来自db group，我爱牛肉火锅，谢谢大家支持。\n"*4})
    votename = "VoteName"
    voteLimit = 1
    max_id = len(candidate)
    t = "单选题"
    description = "这里是描述"
    return render(request, 'vote.html', {'votes': candidate
                                         , "votename": votename
                                         , "voteLimit":voteLimit
                                         , "max_id":max_id
                                         , "type": t
                                         , "description": description
                                         ,})
    # return render(request, 'vote.html')

def card(request):
    u_id = request.session['user_id']  # 获取当前user_id
    votes = []
    e = Entry.objects.filter(user_id=u_id)
    for item in e:
        votes.append(item.vote_id)
    return render_to_response('card.html',{"votes":votes})
# def creat_vote(request):

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
        article = models.Artivle.objects.get(pk=id)
        article.title=title
        article.content = content
        article.save()

    articles = models.Artivle.objects.all()
    return render(request, 'startvote/index.html', {'artilces': articles})

