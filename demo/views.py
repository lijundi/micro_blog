from datetime import timedelta
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.utils.crypto import random
from .serializers import *
from rest_framework.renderers import JSONRenderer
from django.core.mail import send_mail
from micro_blog import settings


# Create your views here.

# 主页面
def index(request):
    return render(request, 'base_index.html')

# 忘记密码页面
def forgetpassword(request):
    return render(request, 'sendmail.html')

# 注册
def signup(request):
    if request.method=='GET':
        return render(request,'regisit.html')
    u = request.POST['u']
    p = request.POST['p']
    e = request.POST['e']
    if User.objects.filter(Q(username=u)|Q(email=e)).count()==0:    #没重
        use=User.objects.create_user(username=u,password=p,email=e)
        use.save()
        return HttpResponse("ok")
    return HttpResponse("error")

# 登陆
def signin(request):
    u = request.POST['u']
    p = request.POST['p']
    user=authenticate(username=u,password=p)
    if user is not None:    #验证通过没
        if user.is_active:  #是否被禁用
            login(request,user)
            return HttpResponse("ok")
        else:
            str="Your account is forbidden!"
    else:
        str="Please check your input!"
        return HttpResponse("invalid")

# 注销
@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect("/")

# 发表推文
@login_required
def post(request):
    content = request.POST['c']
    fuck = request.POST['pic']
    poster = request.user
    p=Post.objects.create(content=content,poster=poster,picture=fuck)
    p.save()
    return HttpResponse(str(p.id))

# 发表评论
@login_required
def comment(request):
    content = request.POST['c']
    poster = request.user
    belongs = request.POST['b']
    c = Comment.objects.create(content=content,poster=poster,belongs_id=belongs)
    c.save()
    n=Notification.objects.create(type="comment",receiver_id=Post.objects.get(id=belongs).poster.id,noti_id=c.id)
    n.save()
    return HttpResponse(str(c.id))

# 发表回复
@login_required
def reply(request):
    content = request.POST['c']
    poster = request.user
    belongs = request.POST['b']
    vic_reply = request.POST['u']
    r = Reply.objects.create(content=content,poster=poster,belongs_id=belongs,vic_reply_id=vic_reply)
    r.save()
    n=Notification.objects.create(type="reply",receiver_id=Comment.objects.get(id=belongs).poster.id,noti_id=r.id)
    n.save()
    return HttpResponse(str(r.id))

# 点赞
@login_required
def like(request):
    liker = request.user
    vic_like = request.POST['v']
    if(Like.objects.filter(liker=liker,vic_like_id=vic_like).count()==0):
        l = Like.objects.create(liker=liker,vic_like_id=vic_like)
        l.save()
        p = Post.objects.get(id=vic_like)
        a=p.likes
        a=a+1
        p.likes=a
        p.save()
        n=Notification.objects.create(type="like",receiver_id=Post.objects.get(id=vic_like).poster.id,noti_id=l.id)
        n.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('liked')

# @
@login_required
def at(request):
    type = request.POST['t']
    belongs_id = request.POST['b']
    ater = request.user
    vic_at = request.POST['v']
    if(User.objects.filter(id=vic_at).count()>0):
        a = At.objects.create(type=type,belongs_id=belongs_id,ater=ater,vic_at_id=vic_at)
        a.save()
        n = Notification.objects.create(type="at", receiver_id=vic_at, noti_id=a.id)
        n.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('error')

# 私信
@login_required
def letter(request):
    sender = request.user
    receiver = request.POST['r']
    content = request.POST['c']
    l = Letter.objects.create(sender=sender,receiver_id=receiver,content=content)
    l.save()
    return HttpResponse('ok')   # 这里后期可能直接改成创建成功的对象

# 关注
@login_required
def focus(request):
    focuser = request.user
    vic_focus = request.POST['v']
    if(Focus_Rela.objects.filter(focuser=focuser,vic_focus_id=vic_focus).count()==0):
        f = Focus_Rela.objects.create(focuser=focuser,vic_focus_id=vic_focus)
        f.save()
        n = Notification.objects.create(type="focus", receiver_id=vic_focus, noti_id=f.id)
        n.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('focused')

# 查看是否关注过
@login_required
def isfocused(request):
    id=request.POST['id']
    u=request.user
    if(Focus_Rela.objects.filter(vic_focus_id=id,focuser=u).count()>0):
        return HttpResponse("yes")
    else:
        return HttpResponse("no")


# 请求指定数目的推文
def get_post_num(request):
    num = int(request.POST['num'])   #请求数量
    userid = request.POST['userid'] #请求指定用户的推文，为空不做限制
    lastid = request.POST['lastid'] #已加载的最后一条推文的id
    if userid!="":
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now(),poster_id=userid).order_by('-time')[:num],many=True)
        else:
            time = Post.objects.get(id=lastid).time
            serializer = PostSerializer(Post.objects.filter(time__lt=time,poster_id=userid).order_by('-time')[:num],many=True)
    else:
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now()).order_by('-time')[:num],many=True)
        else:
            time = Post.objects.get(id=lastid).time
            serializer = PostSerializer(Post.objects.filter(time__lt=time).order_by('-time')[:num],many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 发送找回邮件
def sendmail(request):
    now = timezone.now()
    # 删除过期记录
    outdate = Check_Code.objects.filter(time__lt=now).all()
    outdate.delete()
    # 查看账户是否存在
    r = request.POST['who']
    if User.objects.filter(email=r).count()>0:
        code=random.randint(000000,999999)
        title="微博密码找回邮件"
        msg="你的密码找回地址：\n"+"http://127.0.0.1:8000/verify/?email="+r+"&code="+str(code).zfill(6)+"\n请勿将此邮件泄漏给他人，十五分钟内有效"
        email_from=settings.DEFAULT_FROM_EMAIL
        reciever=[r]
        send_mail(title,msg,email_from,reciever)
        deadline = now +timedelta(minutes=15)
        cc = Check_Code.objects.create(time=deadline,email=r,code=str(code).zfill(6))
        cc.save()
        return HttpResponse("ok")
    else:
        return HttpResponse("error")

# 找回邮件验证
def verify(request):
    email=request.GET['email']
    code=request.GET['code']
    if(Check_Code.objects.filter(code=code,email=email,time__gt=timezone.now()).count()>0):
        return render(request, 'reset_password.html', locals())
    else:
        return HttpResponse("error")

# 重置密码
def reset(request):
    email=request.POST['email']
    code=request.POST['code']
    p=request.POST['p']
    if(Check_Code.objects.filter(code=code,email=email,time__gt=timezone.now()).count()>0):
        a=User.objects.get(email=email)
        a.set_password(p)
        a.save()
        Check_Code.objects.filter(email=email,code=code).delete()
        return HttpResponse("ok")
    else:
        return HttpResponse("error")

# 登陆状态检测
def logstatus(request):
    if request.user.is_authenticated:  #判断是否登陆
        return HttpResponse("yes")
    #没登陆
    else:
        return HttpResponse("no")

# 请求用户信息
def userinfo(request):
    if request.user.is_authenticated:
        user = request.user
        guanzhu = Focus_Rela.objects.filter(focuser=user).count()
        fensi = Focus_Rela.objects.filter(vic_focus=user).count()
        name = user.username
        id=user.id
        tuiwen = Post.objects.filter(poster=user).count()
        json_dict = {'guanzhu':guanzhu,'fensi':fensi,'name':name,'tuiwen':tuiwen,'id':id}
        return JsonResponse(json_dict, json_dumps_params={'ensure_ascii': False})
    else:
        return HttpResponse("error")

# 通过id请求用户信息
def userinfoid(request):
    id=request.POST['id']
    if User.objects.filter(id=id).count()>0:
        user = User.objects.get(id=id)
        guanzhu = Focus_Rela.objects.filter(focuser=user).count()
        fensi = Focus_Rela.objects.filter(vic_focus=user).count()
        name = user.username
        tuiwen = Post.objects.filter(poster=user).count()
        json_dict = {'guanzhu':guanzhu,'fensi':fensi,'name':name,'tuiwen':tuiwen}
        return JsonResponse(json_dict, json_dumps_params={'ensure_ascii': False})
    else:
        return HttpResponse("error")

# 获取指定推文下的评论
def get_comment_post(request):
    id=request.POST['id']
    c=Comment.objects.filter(belongs_id=id).order_by('-time')
    serializer = CommentSerializer(c,many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 阅读量加一
def hitpp(request):
    id=request.POST['id']
    x = Post.objects.get(id=id)
    a = x.hits + 1
    x.hits = a
    x.save()
    return HttpResponse("ok")

# 获取指定评论下的回复
def get_reply_comment(request):
    id=request.POST['id']
    c=Reply.objects.filter(belongs_id=id).order_by('-time')
    serializer = ReplySerializer(c,many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取指定推文
def get_post(request):
    id=request.POST['id']
    c=Post.objects.get(id=id)
    serializer=PostSerializer(c)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取指定评论
def get_comment(request):
    id=request.POST['id']
    c=Comment.objects.get(id=id)
    serializer=CommentSerializer(c)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取指定回复
def get_reply(request):
    id=request.POST['id']
    c=Reply.objects.get(id=id)
    serializer=ReplySerializer(c)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取@内容
def get_content_at(request):
    id=request.POST['id']
    at=At.objects.get(id=id)
    u=at.ater
    x={'id':u.id,'username':u.username,'email':u.email}
    if(at.type=="comment"):
        c = Comment.objects.get(id=at.belongs_id).content
        json_dict = {'content': c,'person':x}
    if(at.type=="reply"):
        c = Reply.objects.get(id=at.belongs_id).content
        json_dict = {'content': c,'person':x}
    if(at.type=='post'):
        c = Post.objects.get(id=at.belongs_id).content
        json_dict = {'content': c,'person':x}
    return JsonResponse(json_dict, json_dumps_params={'ensure_ascii': False})


# 获取某人所有推文
def get_post_poster(request):
    id = request.POST['id']
    serializer = PostSerializer(Post.objects.filter(poster_id=id).order_by('-time'), many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取某人所有通知
@login_required
def get_noti_receiver(request):
    u=request.user
    serializer = NotificationSerializer(Notification.objects.filter(receiver=u).order_by('-id'), many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取a和b私信记录
def get_letter(request):
    a_=request.POST['a']
    b_=request.POST['b']
    serializer = LetterSerializer(Letter.objects.filter(Q(sender_id=a_,receiver_id=b_)|Q(sender_id=b_,receiver_id=a_)).order_by('time'), many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取某人的所有粉丝
def get_fans(request):
    id=request.POST['id']
    serializer = Focus_RelaSerializer(Focus_Rela.objects.filter(vic_focus_id=id), many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取某人的所有关注对象
def get_focus(request):
    id=request.POST['id']
    serializer = Focus_RelaSerializer(Focus_Rela.objects.filter(focuser_id=id), many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取点赞
def get_like(request):
    id=request.POST['id']
    c=Like.objects.get(id=id)
    serializer = LikeSerializer(c)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取关注
def get_focus_one(request):
    id=request.POST['id']
    c=Focus_Rela.objects.get(id=id)
    serializer = Focus_RelaSerializer(c)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取最热推文
def get_post_hot(request):
    num = int(request.POST['num'])   #请求数量
    userid = request.POST['userid'] #请求指定用户的推文，为空不做限制
    lastid = request.POST['lastid'] #已加载的最后一条推文的id
    if userid!="":
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now(),poster_id=userid).order_by('-hits','-time')[:num],many=True)
        else:
            hits = Post.objects.get(id=lastid).hits
            time = Post.objects.get(id=lastid).time
            if(Post.objects.filter(likes__lt=hits).count()==0):
                serializer = PostSerializer(Post.objects.filter(hits__lte=hits,poster_id=userid,time__lt=time).order_by('-hits','-time')[:num],many=True)
            else:
                if (Post.objects.filter(hits=hits,poster_id=userid, time__lt=time).count() != 0):
                    serializer = PostSerializer(
                        Post.objects.filter(hits=hits,poster_id=userid, time__lt=time).order_by('-hits', '-time')[:num], many=True)
                    j = JSONRenderer().render(serializer.data)
                    return HttpResponse(j, content_type="application/json")
                if(Post.objects.filter(hits__lt=hits,time__gt=time,poster_id=userid,time__lt=timezone.now()).count()==0):
                    serializer = PostSerializer(Post.objects.filter(hits__lt=hits,time__lt=timezone.now(),poster_id=userid).order_by('-hits','-time')[:num],many=True)
                else:
                    serializer = PostSerializer(Post.objects.filter(Q(hits__lt=hits)&Q(time__gt=time),poster_id=userid,time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)

    else:
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now()).order_by('-hits','-time')[:num],many=True)
        else:
            hits = Post.objects.get(id=lastid).hits
            time = Post.objects.get(id=lastid).time
            if(Post.objects.filter(likes__lt=hits).count()==0):
                serializer = PostSerializer(Post.objects.filter(hits__lte=hits,time__lt=time).order_by('-hits','-time')[:num],many=True)
            else:
                if(Post.objects.filter(hits=hits,time__lt=time).count()!=0):
                    serializer = PostSerializer(Post.objects.filter(hits=hits,time__lt=time).order_by('-hits','-time')[:num],many=True)
                    j = JSONRenderer().render(serializer.data)
                    return HttpResponse(j, content_type="application/json")
                if(Post.objects.filter(hits__lt=hits,time__gt=time,time__lt=timezone.now()).count()==0):
                    serializer = PostSerializer(Post.objects.filter(hits__lt=hits,time__lt=timezone.now()).order_by('-hits','-time')[:num],many=True)
                else:
                    serializer = PostSerializer(Post.objects.filter(hits__lt=hits,time__gt=time,time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 获取最受欢迎推文
def get_post_like(request):
    num = int(request.POST['num'])   #请求数量
    userid = request.POST['userid'] #请求指定用户的推文，为空不做限制
    lastid = request.POST['lastid'] #已加载的最后一条推文的id
    if userid!="":
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now(),poster_id=userid).order_by('-likes','-time')[:num],many=True)
        else:
            likes = Post.objects.get(id=lastid).likes
            time = Post.objects.get(id=lastid).time
            if(Post.objects.filter(likes__lt=likes).count()==0):
                serializer = PostSerializer(Post.objects.filter(Q(likes__lte=likes)&Q(time__lt=time),poster_id=userid).order_by('-likes','-time')[:num],many=True)
            else:
                if (Post.objects.filter(likes=likes,poster_id=userid, time__lt=time).count() != 0):
                    serializer = PostSerializer(
                        Post.objects.filter(likes=likes,poster_id=userid, time__lt=time).order_by('-likes', '-time')[:num], many=True)
                    j = JSONRenderer().render(serializer.data)
                    return HttpResponse(j, content_type="application/json")
                if(Post.objects.filter(likes__lt=likes,time__gt=time,poster_id=userid,time__lt=timezone.now()).count()==0):
                    serializer = PostSerializer(Post.objects.filter(likes__lt=likes,poster_id=userid,time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
                else:
                    serializer = PostSerializer(Post.objects.filter(Q(likes__lt=likes)&Q(time__gt=time),poster_id=userid,time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
    else:
        if lastid=="":
            serializer = PostSerializer(Post.objects.filter(time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
        else:
            likes = Post.objects.get(id=lastid).likes
            time = Post.objects.get(id=lastid).time
            if(Post.objects.filter(likes__lt=likes).count()==0):
                serializer = PostSerializer(Post.objects.filter(Q(likes__lte=likes)&Q(time__lt=time)).order_by('-likes','-time')[:num],many=True)
            else:
                if (Post.objects.filter(likes=likes, time__lt=time).count() != 0):
                    serializer = PostSerializer(
                        Post.objects.filter(likes=likes, time__lt=time).order_by('-likes', '-time')[:num], many=True)
                    j = JSONRenderer().render(serializer.data)
                    return HttpResponse(j, content_type="application/json")
                if(Post.objects.filter(likes__lt=likes,time__gt=time,time__lt=timezone.now()).count()==0):
                    serializer = PostSerializer(Post.objects.filter(likes__lt=likes,time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
                else:
                    serializer = PostSerializer(Post.objects.filter(Q(likes__lt=likes)&Q(time__gt=time),time__lt=timezone.now()).order_by('-likes','-time')[:num],many=True)
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j, content_type="application/json")

# 判断有没有这个人
def atisexist(request):
    name=request.POST['name']
    if(User.objects.filter(username=name).count()>0):
        u=User.objects.get(username=name)
        serializer = UserSerializer(u)
        j = JSONRenderer().render(serializer.data)
        return HttpResponse(j, content_type="application/json")
    else:
        return HttpResponse('error')

# 获取准备发推文基类id
def tmppostid(request):
    return HttpResponse(str(Base_Post.objects.last().id+1))

# 个人主页跳转
def private_index_go(request):
    id=request.GET['id']
    return render(request, 'private_index.html', locals())

# 通知页面跳转
def notify_go(request):
    return render(request, 'notify.html')

# 私信页面跳转
def letter_go(request):
    return render(request, 'letter.html')

# 获取所有私信对象
@login_required
def getlettervic(request):
    u=request.user
    p=Letter.objects.filter(receiver=u)
    c=[]
    n=[]
    for x in p:
        if User.objects.get(id=x.sender.id).username not in c:
            c.append(User.objects.get(id=x.sender.id).username)
            n.append(User.objects.get(id=x.sender.id).id)
    json_dict = {'name': c,'id':n}
    return JsonResponse(json_dict, json_dumps_params={'ensure_ascii': False})

# 测试
def lll(request):
    serializer=PostSerializer(Post.objects.get(id=4))
    j = JSONRenderer().render(serializer.data)
    return HttpResponse(j,content_type="application/json")

