from django.db import models


class Artivle(models.Model):
    title = models.CharField(max_length=32,default='title')
    content = models.TextField(null=True)
    pub_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.title



# Create your models here.
class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)


class Vote(models.Model):
    vote_id = models.IntegerField(primary_key=True)  # 自增主键
    vote_name = models.CharField(max_length=50)
    vote_type = models.IntegerField()  # 多选,单选
    vote_state = models.IntegerField()  # 投票状态
    vote_description = models.TextField()  # 投票描述
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    option_size = models.IntegerField()  # 选项数目
    option_content = models.TextField()  # 选项内容,可能为一个json文件

#     # options_content
#
#
# class Entry(models.Model):  # 公钥,投票活动id,将人和投票连接起来,并保持user_id的匿名性
#     # public_key = models.CharField(max_length=300)  # 不能连接到 user_id,单向性保证了安全性
#     user_id = models.ForeignKey(User, to_field=User.user_id,on_delete=models.CASCADE)  # 用户id
#     vote_id = models.ForeignKey(Vote,to_field=Vote.vote_id,on_delete=models.CASCADE)  # 外键
    # option = models.IntegerField()
#
#
# class Key(models.Model):  # 一对多,一个用户可以有多个公私钥对
#     user_id = models.ForeignKey(User, to_field=User.user_id,on_delete=models.CASCADE)  # 用户id
#     public_key = models.CharField(max_length=300)


#class Result(models.Model):


#admin.site.register(User)
