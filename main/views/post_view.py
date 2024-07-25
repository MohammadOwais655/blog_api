from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
import random

from ..pagination import PageNumberPaginationPost
from ..models import Post, UserSuggestionTopic
from ..serializers import PostSerializer, UserSuggestionTopicSerializer
from ..utils import (image_upload, generate_tag_suggestions, 
                     extract_topics_from_post, generate_topic_suggestions,
                     chatgpt_engine,
                     )


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def post_create_view(request):
    image = request.data.get('image', None)
    if image is None:
        return Response({'error': 'image required for creating post'}, status=400)

    topics = extract_topics_from_post(request.data.get('title'), request.data.get('content'))
    print("keywords: ", topics)
    try:
        user_seggestion = UserSuggestionTopic.objects.get(user=request.user)
    except:
        user_seggestion = None

    if user_seggestion is None:
        user_suggestion_serializer = UserSuggestionTopicSerializer(data={'topic':topics}, context={'user': request.user})
        user_suggestion_serializer.is_valid(raise_exception=True)
        user_suggestion_serializer.save()
    else:
        user_suggestion_serializer = UserSuggestionTopicSerializer(user_seggestion, data={'topic':topics}, partial=True)
        user_suggestion_serializer.is_valid(raise_exception=True)
        user_suggestion_serializer.save()

    image_id = request.data.get('title').replace(' ', '')
    image_id = image_id.lower()
    res = image_upload(image, 'post_images', public_id=image_id)

    if res is None:
        return Response({'error': 'image of post is not uploaded. try again'}, status=500)

    request.data['image_url'] = res.get('secure_url')
    request.data['image_id'] = res.get('public_id')
    
    serializer = PostSerializer(data=request.data, context={'user': request.user})
    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data)
    return Response(serializer.errors)


@permission_classes([IsAuthenticated])
@api_view(['PUT', 'PATCH'])
def post_update_view(request, post_id):
    try:
        post = Post.objects.get(user_id=request.user.id, pk=post_id)
    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=400)
    
    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def post_delete_view(request, post_id):
    try:
        post = Post.objects.get(user_id=request.user.id, pk=post_id)
    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=400)
    
    post.delete()
    return Response({'message': 'Post is deleted'})

    


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def singel_post_view(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=400)
    
    serializer = PostSerializer(post)
    return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def tags_post_view(request):
    tags = request.GET.get('tags').split(',')
    tags_list = [tag.strip() for tag in tags]
    # print(type(tags))
    # print(tags)
    query = Q()
    for tag in tags_list:
        query |= Q(tags__contains=[tag])
    print("Query: ", query)
    posts = Post.objects.filter(query).distinct()
    # print("Post : ", posts)
    paginator = PageNumberPaginationPost()
    paginated_posts = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(paginated_posts, many=True)
    return paginator.get_paginated_response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def all_post_view(request):
    posts = Post.objects.all()
    paginator = PageNumberPaginationPost()
    paginated_posts = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(paginated_posts, many=True)
    # print(serializer.data)
    # print("ok at this line 3")
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def suggestions_tags_topics(request):
    # user_prompt = request.data.get('prompt')
    # if user_prompt:
    #     response = chatgpt_engine(user_prompt).replace('\n\n', '\n').split('\n')
        
    #     return Response({'data': response}, status=200)
    user = request.user
    posts = Post.objects.filter(user=user) ## get query set and multiple instance of post
    tags_list = set()
    for post in posts:
        tags_list.update(post.tags)
    # tags_list = list(tags_list)
    
    tags_suggestion = generate_tag_suggestions(tags_list)
    print(type(tags_suggestion))
    topics = generate_topic_suggestions(tags_suggestion or [])
    # topics = UserSuggestionTopic.objects.filter(user=user).order_by('?')[:10]
    # print(topics)
    # serializer = UserSuggestionTopicSerializer(topics, many=True)
    data = {
        'tags_suggestion': tags_suggestion,
        'topics': topics,
    }
    return Response(data)
    # return Response({'error': 'prompt message required'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggest_content(request):
    title = request.data.get('title')

    response = chatgpt_engine(title)

    return Response({'content': response})