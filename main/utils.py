from django.utils import timezone
from django.conf import settings
import cloudinary
import cloudinary.api
import cloudinary.uploader
import os
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .models import User

import openai


def cloudinary_config():
    cloudinary.config(
        cloud_name = os.getenv('CLOUD_NAME'),
        api_key = os.getenv('API_KEY'),
        api_secret = os.getenv('API_SECRET_KEY'),
        secure = True
    )


def image_upload(file, folder_name, public_id=None):
    cloudinary_config()
    res = cloudinary.uploader.upload(
        file,
        public_id = public_id,
        asset_folder = folder_name
    )

    return res


def delete_image(avatar_id):
    cloudinary_config()
    res = cloudinary.api.delete_resources(public_ids=avatar_id)
    return res


def geterate_jwt_token(user):
    payload = {
        'id': user.id,
        'email': user.email,
        'exp': timezone.now() + timezone.timedelta(days=1),
        'iat': timezone.now()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def validate_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        user = User.objects.get(pk=user_id)
        return user
    except (ExpiredSignatureError, InvalidTokenError, User.DoesNotExist) as e:
        print("Token Validation Error: ", str(e))
        return None
    

def chatgpt_engine(user_content):
    # system_content = "You are a travel agent. Be descriptive and helpful."
    # user_content = "Suggest the topic for blogging on IT"

    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    chat_completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            # {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=128,
    )

    response = chat_completion.choices[0].message.content
    print("AI/ML API:\n", response)
    return response