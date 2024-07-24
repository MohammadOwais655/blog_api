from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from ..serializers import UserSerializer
from ..utils import geterate_jwt_token, image_upload
from ..models import BlacklistedToken, User


@api_view(['POST'])
def register(request):
    print(request.data)
    avatar = request.data.get('avatar')
    if avatar is None:
        return Response({'error': 'avatar image is required!'}, status=400)
    avatar_id = request.data.get('email').replace('@', '').replace('.', '')
    res = image_upload(avatar, 'user_images', public_id=avatar_id)
    request.data['avatar_url'] = res.get('secure_url')
    request.data['avatar_id'] = res.get('public_id')
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = authenticate(email=request.data['email'], password=request.data['password'])
        if user is not None:
            token = geterate_jwt_token(user)
            data = {
                'login': True,
                'token': token
            }
            return Response(data, status=200)
        return Response({'error': 'this is not a valid user'}, status=401)
    return Response({'error': serializer.errors}, status=400)



@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)
    if user is not None:
        token = geterate_jwt_token(user)
        data = {
            'login': True,
            'token': token
        }
        return Response(data, status=200)
    
    return Response({'error': 'invalid credintials'}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    print(request)
    token = request.META.get('HTTP_AUTHORIZATION').split()[1]
    blacklist = BlacklistedToken.objects.create(token=token)
    blacklist.save()
    return Response({'message': 'Logout successfully'}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user_id = request.user.id
    try:
        user = User.objects.get(pk=user_id)
        serializer = UserSerializer(user)
        return Response({'data': serializer.data}, status=200)
    except User.DoesNotExist as e:
        print(str(e))
        return Response({'error': str(e)}, status=404)