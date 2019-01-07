from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class Focus_RelaSerializer(serializers.ModelSerializer):
    focuser=UserSerializer()
    vic_focus=UserSerializer()
    class Meta:
        model = Focus_Rela
        fields = ('focuser', 'vic_focus')

class LikeSerializer(serializers.ModelSerializer):
    liker=UserSerializer()
    class Meta:
        model = Like
        fields = ('liker', 'vic_like')

class AtSerializer(serializers.ModelSerializer):
    ater=UserSerializer()
    vic_at=UserSerializer()
    class Meta:
        model = At
        fields = ('type', 'belongs_id', 'ater', 'vic_at')

class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ('sender', 'receiver', 'time', 'content')

class NotificationSerializer(serializers.ModelSerializer):
    receiver=UserSerializer()
    class Meta:
        model = Notification
        fields = ('type', 'noti_id','receiver')

class CommentSerializer(serializers.ModelSerializer):
    poster=UserSerializer()
    class Meta:
        model = Comment
        fields = ('id', 'content', 'time', 'poster')

class ReplySerializer(serializers.ModelSerializer):
    poster=UserSerializer()
    vic_reply=UserSerializer()
    class Meta:
        model = Reply
        fields = ('id', 'content', 'time', 'poster','vic_reply')

class PostSerializer(serializers.ModelSerializer):
    poster = UserSerializer()
    class Meta:
        model = Post
        fields = ('id', 'hits', 'likes', 'content', 'time', 'poster','picture')
