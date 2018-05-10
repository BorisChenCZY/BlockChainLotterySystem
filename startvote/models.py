from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Artivle(models.Model):
    title = models.CharField(max_length=32,default='title')
    content = models.TextField(null=True)
    pub_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.title


class Vote(models.Model):
    vote_id = models.IntegerField(primary_key=True)  # 自增主键
    vote_name = models.CharField(max_length=50)
    vote_type = models.IntegerField(null=True) # 多选,单选 1:单选 2：多选
    vote_state = models.IntegerField(null=True)  # 投票状态，状态编码，1：未开始 2：进行中 3：已结束
    vote_target = models.TextField(null=True)  # 一个hash值
    vote_description = models.TextField(null=True)  # 投票描述
    is_checkable = models.BooleanField(default=True)  # 是否可以查看投票结果，默认可以
    is_opened = models.BooleanField(default=False)  # 是否需要认证，默认不需要
    creat_time = models.DateTimeField(null=True)  # 创建时间
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    # option_size = models.IntegerField(null=True)  # 选项数目
    # option_content = models.TextField(null=True)  # 选项内容,可能为一个json文件

#     # options_content
#
#
class Entry(models.Model):  # 公钥,投票活动id,将人和投票连接起来,并保持user_id的匿名性

    # public_key = models.CharField(max_length=300)  # 不能连接到 user_id,单向性保证了安全性
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)  # 用户id
    vote_id = models.ForeignKey('Vote',on_delete=models.CASCADE)  # 外键
    condition = models.BooleanField(default=False)  # 投票状态，状态编码，true：已投 false：未投
    identity = models.IntegerField(default=1)  # 身份，可能是参与者(1)，也可能是发起者对应我参与的，我发起的(2)
    # option = models.IntegerField()
#
#
# class Key(models.Model):  # 一对多,一个用户可以有多个公私钥对
#     user_id = models.ForeignKey(User, to_field=User.user_id,on_delete=models.CASCADE)  # 用户id
#     public_key = models.CharField(max_length=300)

class Selection(models.Model):

    selection_id = models.IntegerField(primary_key=True)  # 自增主键
    vote_id = models.ForeignKey(Vote, on_delete=models.CASCADE,null=True,blank=True,default=None)  # 外键
    title = models.CharField(max_length=50,null=True)  #候选人标题
    simple_detail = models.TextField(null=True)   #候选人简单描述
    detail = models.TextField(null=True)   #候选人详细描述
    img = models.ImageField(null=True)


class local_Key_pool(models.Model):  # 公私钥池
    key_id = models.IntegerField(primary_key=True)
    public_key = models.CharField(max_length=300,null=False)
    private_key = models.CharField(max_length=300, null=False)
    statue = models.BooleanField(default=False) # 是否被使用 0：未被使用 1： 使用中



admin.site.register(Vote)
admin.site.register(Entry)
admin.site.register(Selection)
admin.site.register(local_Key_pool)
#
#  fd