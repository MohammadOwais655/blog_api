from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils import validate_jwt_token
from .models import BlacklistedToken

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self.get_token_from_request(request)
        if token is None:
            return
        
        if BlacklistedToken.objects.filter(token=token).exists():
            raise AuthenticationFailed("Token is invalid or expired")
        
        user = validate_jwt_token(token)
        if user is None:
            raise AuthenticationFailed("Token is invalid or expired!")
        
        return (user, token)


    def get_token_from_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def authenticate_header(self, request):
        return super().authenticate_header(request)