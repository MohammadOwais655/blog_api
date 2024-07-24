from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import User, Post


class UserSerializer(ModelSerializer):
    avatar_id = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar_url', 'avatar_id', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        print("passowrd: ", password)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class PostSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = serializers.ListField(
        child = serializers.CharField(),
    )
    image_id = serializers.CharField(write_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'content','image_url', 'image_id', 'user', 'tags']


    def create(self, validated_data):
        user = self.context.get('user')
        print("user:", user)
        tags = validated_data.pop('tags')[0].split(',') if validated_data.get('tags') else ''
        post = Post.objects.create(user=user, **validated_data)
        tags_list = [tag.strip() for tag in tags]
        post.tags = tags_list
        post.save()
        return post
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')[0].split(',') if validated_data.get('tags') else ''
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        tags_list = [tag.strip() for tag in tags]
        existing_tags = instance.tags
        new_tags_list = list(set(tags_list + existing_tags))
        instance.tags = new_tags_list
        instance.save()
        return instance
