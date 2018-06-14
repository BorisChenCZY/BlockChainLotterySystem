from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django import forms
from django.contrib import sessions
from . import models
from .models import User,Vote,Entry,Selection
from block import block_hashfunc
import dateutil.parser
import block.model_block as bm
import datetime
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
import json
import settings
from startvote.ECDSA import *

# context = {'isLogin': True,'username':''}
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
            print(username, password)
            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request,user)
                request.session['username'] = user.username
                print("logined in")

                return render(request, 'index.html')
            else:
                print("password wrong")
                return render(request, "login.html")

#注册
def signup(request):
    return render(request, 'signup.html')

def logout(request):
    #清理cookie里保存username
    auth.logout(request)
    return render(request, "login.html")

def form(request):
   # print(request.session['username'])
    # if request.session['username'] != "blockchain":
    #     return HttpResponse("No authority")
    # 先检验登录状态
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'form.html')
        else:
            return render(request, 'login.html')
    else:
        # hash 校验
        d = datetime.datetime.now()

        if Vote.objects.filter(vote_target=block_hashfunc.hash(str(request.POST.get("vote_name")+str(d)).encode())):
            return HttpResponse(" this vote has been exist!")
        else:
            vote = Vote()
            entry = Entry()
            vote.creat_time = datetime.datetime.now()
            vote.vote_name = request.POST.get("vote_name")
            if request.FILES.get("vote_img"):
                vote.vote_img = request.FILES.get("vote_img")
            vote.vote_description = request.POST.get("vote_description")
            vote.start_time = request.POST.get("start_time")
            vote.end_time = request.POST.get("end_time")


            if dateutil.parser.parse(request.POST.get("start_time")) > d : # 未开始
                vote.vote_state = 1
            elif dateutil.parser.parse(request.POST.get("end_time")) > d : # 进行中
                vote.vote_state = 2
            else: # 已结束
                vote.vote_state = 3
            if request.POST.get("vote_anonymity"):
                vote.vote_anonymity = True
            else:
                vote.vote_anonymity = False
            if int(request.POST.get("is_opened")) == 1:  # 是否是公开投票
                vote.is_opened = True
            else:
                vote.is_opened = False
            if request.POST.get("is_checkable") == "yes":  # 是否展示投票结果给参与者
                vote.is_checkable = True
            else:
                vote.is_checkable = False
            vote.vote_optionable_num = int(request.POST.get("vote_optionable_num"))

            vote_target = block_hashfunc.hash((str(vote.vote_name)+str(d)).encode())
            vote.vote_target = vote_target
            vote.save()

            options_list = request.POST.getlist("options")
            vote_details = request.POST.getlist("vote_details")
            attachments = request.FILES.getlist("attachments")
            for i in range(len(options_list)):
                print(i)
                seletion = Selection()
                seletion.vote_id = Vote.objects.get(vote_target=vote_target)
                seletion.title = options_list[i]
                seletion.simple_detail = "这个人很懒，什么都没写"
                seletion.detail = vote_details[i]
                # path＝default_storage.save（，ContentFile（image.read()））
                # if attachments:
                seletion.img = attachments[i]

                seletion.save()


            entry.user_id = auth.get_user(request)
            entry.vote_id = Vote.objects.get(vote_target=vote_target)
            entry.identity = 2  # 表示发起人
            entry.condition = False
            entry.save()

            return render_to_response('share.html', {"vote_target": str(vote_target)})



def vote(request, target):
    vote = Vote.objects.filter(vote_target=target).get()

    if vote.is_opened or request.user.is_authenticated:
        br = bm.BlockReader()
        on_chain_result = br.getVoteResult(target)
        # print(vote.vote_name)
        on_web_list = Selection.objects.filter(vote_id=vote)
        candidate = []
        for option in on_web_list:
            id = option.selection_id
            new_dict = {}
            new_dict["id"] = option.selection_id
            new_dict["title"] = option.title
            new_dict["simple"] = option.simple_detail
            new_dict["detail"] = option.detail
            new_dict["img"] = option.img
            new_dict["voteNum"] = 0
            candidate.append(new_dict)
        if not on_chain_result:
            Max = 0
        else:
            Max = max([result[1] for result in on_chain_result])
        for result in on_chain_result:
            candidate[result[0] - 1]["voteNum"] = result[1]
            candidate[result[0] - 1]["width"] = result[1] * 80 / float(Max)
        votename = vote.vote_name
        voteLimit = vote.vote_optionable_num
        max_id = len(candidate)
        t = str(max_id) + "选" + str(vote.vote_optionable_num)
        description = vote.vote_description
        miner_list = br.getMinerList()
        format_miner_list = [m[0] for m in miner_list]
        print(format_miner_list)
        return render(request, 'vote.html', {'candidate': candidate
            , "vote": vote
            , "voteLimit": voteLimit
            , "max_id": max_id
            , "type": t
            , "description": description
            , "target": target
            , "miner_list": format_miner_list})
    else:

        return render(request, 'login.html')
    # if vote.is_opened or request.user.is_authenticated:
    #     br = bm.BlockReader()
    #     on_chain_result = br.getVoteResult(target)
    #     # print(vote.vote_name)
    #     on_web_list = Selection.objects.filter(vote_id=vote)
    #     candidate = []
    #     for option in on_web_list:
    #         id = option.selection_id
    #         new_dict = {}
    #         new_dict["id"] = option.selection_id
    #         new_dict["title"] = option.title
    #         new_dict["simple"] = option.simple_detail
    #         new_dict["detail"] = option.detail
    #         new_dict["img"] = option.img
    #         new_dict["voteNum"] = 0
    #         candidate.append(new_dict)
    #     if not on_chain_result:
    #         Max = 0
    #     else:
    #         Max = max([result[1] for result in on_chain_result])
    #     for result in on_chain_result:
    #         candidate[result[0] - 1]["voteNum"] = result[1]
    #         candidate[result[0] - 1]["width"] = result[1] * 80 / float(Max)
    #     votename = vote.vote_name
    #     voteLimit = vote.vote_optionable_num
    #     max_id = len(candidate)
    #     t = str(max_id) + "选" + str(vote.vote_optionable_num)
    #     description = vote.vote_description
    #     miner_list = br.getMinerList()
    #     format_miner_list = [m[0] for m in miner_list]
    #     print(format_miner_list)
    #     return render(request, 'vote.html', {'candidate': candidate
    #         , "vote": vote
    #         , "voteLimit": voteLimit
    #         , "max_id": max_id
    #         , "type": t
    #         , "description": description
    #         , "target": target
    #         , "miner_list": format_miner_list})
    # else:
    #
    #     return render(request, 'login.html')


def card(request):
    result_list =[]
    user = auth.get_user(request)
    e = Entry.objects.filter(user_id=user)
    for item in e:
        vote_condition = {}
        if item.condition:
            vote_condition["condition"] = "已投"
        else:
            vote_condition["condition"] = "未投"
        vote_condition["vote"] = item.vote_id
        vote_condition["target"] = item.vote_id.vote_target
        result_list.append(vote_condition)
    return render_to_response('card.html',{"result_list":result_list})


def share(request):
    return  render(request,'startvote/share.html')

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
        article.title = title
        article.content = content
        article.save()

    articles = models.Artivle.objects.all()
    return render(request, 'startvote/index.html', {'artilces': articles})

def fold_demo(request):
    if request.method == 'GET':
        return render(request, 'fold_demo.html', {"Web_pub": settings.PUBLIC_KEY})
    elif request.method == 'POST':
        # msg = request.POST.get('msg')
        # print("msg:", msg)
        # signature = request.POST.get('signature')
        # print("sig:", signature)
        # pub_key = request.POST.get('pub_key')
        # print("pubkey:", pub_key)
        # prv = request.POST.get('pri_key')
        # cv = Curve.get_curve('secp256k1')
        # signer = ECDSA()
        # prv = hashlib.md5(prv.encode()).hexdigest()
        # print("prv:", prv)
        # prv_key = ECPrivateKey(int(prv, 16), cv)
        # pub = ECPublicKey(cv.decode_point(bytes.fromhex(pub_key)))
        # pub_key = prv_key.get_public_key()
        # print("pub_key:", pub_key)
        # print("pub:", pub)
        # sig = bytes.fromhex(signature)
        # msg = msg.encode()
        # print(prv_key)
        # print(sig)
        # print(signer.sign(msg, prv_key))
        # veri = signer.verify(msg, sig, pub_key)
        if(request.POST.get('pub_key')):
            fake_pub = request.POST.get('pub_key')
            print(fake_pub)
            fake_sign = blind_signature(fake_pub)
            print(fake_sign)
            return HttpResponse(fake_sign)
        else:
            m = request.POST.get('m')
            c = request.POST.get('c')
            s = request.POST.get('s')
            print(blind_verify(m, c, s))
            return HttpResponse(1)

#获得单个block内的信息
def single_block_info(request):
    block_id = request.POST.get("id", 0)
    br = bm.BlockReader()
    block = br.getBlock(block_id)
    infos = br.getSingleBlockInfo(block_id)
    title = ["target", "pubkey", "selection", "timestamp"]
    title0 = ["Id", "hash", "prehash", "vote_num", "generator"]
    format_infos = []
    format_block = []
    for i,b in enumerate(block):
        format_block.append((title0[i], b))
    for i in infos:
        i = list(i)
        i[0] = i[0][:16]
        i[1] = i[1][:16]
        dateArray = datetime.datetime.utcfromtimestamp(i[3])
        i[3] = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        format_infos.append(i)
    return render(request, 'single_block_info.html', {'block': format_block,'infos': format_infos, 'title': title,'title0': title0})

#获得block chain的信息
def block_info(request):
    br = bm.BlockReader()
    blocks = br.getBlockInfos()
    title = ["Id", "hash", "prehash", "vote_num", "generator"]
    format_blocks = []
    for b in blocks:
        b = list(b)
        b[1] = b[1][:32]   #截取哈希的前32位
        b[2] = b[2][:32]
        format_blocks.append(b)
    return render(request, 'block_info.html', {'blocks': format_blocks, 'title': title})

def real_time_result(request):

    if request.method != "POST":
        return HttpResponse("404 hhh")
    else:
        result= dict(request.POST)
        # print(result)
        url = result["url"][0]
        target = url[url.find("b"):]

        br = bm.BlockReader()
        on_chain_result = br.getVoteResult(target)
        response_data = dict(on_chain_result)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

#获取投票服务器的公钥
def public_key(request):
    return HttpResponse(settings.PUBLIC_KEY)

#服务器对公钥签名
def signature(request):
    #TODO 判断是否有资格签名
    if request.method == 'POST':
        fake_pubkey = request.POST.get('fake_pubkey')
        
        pass



def page_not_found(request):
    return  render(request,'startvote/error.html');