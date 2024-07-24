from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from ..pagination import PageNumberPaginationPost
from ..models import Post
from ..serializers import PostSerializer
from ..utils import image_upload


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def post_create_view(request):
    image = request.data.get('image', None)
    if image is None:
        return Response({'error': 'image required for creating post'}, status=400)

    image_id = request.data.get('title').replace(' ', '')
    # print(type(image_id))
    image_id = image_id.lower()
    res = image_upload(image, 'post_images', public_id=image_id)
    request.data['image_url'] = res.get('secure_url')
    request.data['image_id'] = res.get('public_id')
    # request.data['user'] = request.user
    # print('request data: ', request.data)
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
