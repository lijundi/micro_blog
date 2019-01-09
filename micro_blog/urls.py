"""micro_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from demo import views


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^signup$', views.signup),
    url(r'^signin$', views.signin),
    url(r'^signout$', views.signout),
    url(r'^post$', views.post),
    url(r'^comment$', views.comment),
    url(r'^reply$', views.reply),
    url(r'^at$', views.at),
    url(r'^like$', views.like),
    url(r'^letter$', views.letter),
    url(r'^getletter$', views.get_letter),
    url(r'^focus$', views.focus),
    url(r'^isfocused$', views.isfocused),
    url(r'^forgetpassword$', views.forgetpassword),
    url(r'^sendmail$', views.sendmail),
    url(r'^logstatus$', views.logstatus),
    url(r'^userinfo$', views.userinfo),
    url(r'^userinfoid$', views.userinfoid),
    url(r'^getpost$', views.get_post_num),
    url(r'^gethotpost$', views.get_post_hot),
    url(r'^getlikepost$', views.get_post_like),
    url(r'^getpostposter$', views.get_post_poster),
    url(r'^getnotireceiver$', views.get_noti_receiver),
    url(r'^getcontentat$', views.get_content_at),
    url(r'^verify', views.verify),
    url(r'^reset$', views.reset),
    url(r'^getfans$', views.get_fans),
    url(r'^getfocus$', views.get_focus),
    url(r'^getcommentpost$', views.get_comment_post),
    url(r'^getreplycomment$', views.get_reply_comment),
    url(r'^getcomment$', views.get_comment),
    url(r'^getreply$', views.get_reply),
    url(r'^getlike$', views.get_like),
    url(r'^getfocusone$', views.get_focus_one),
    url(r'^hits$', views.hitpp),
    url(r'^privatego', views.private_index_go),
    url(r'^notifygo$', views.notify_go),
    url(r'^lettergo$', views.letter_go),
    url(r'^idgetpost$', views.get_post),
    url(r'^atisexist$', views.atisexist),
    url(r'^gettmpid$', views.tmppostid),
    url(r'^getlettervic$', views.getlettervic),
    url(r'^lll', views.lll),
]
