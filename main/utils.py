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
        # prompt = user_content,
        temperature=0.7,
        max_tokens=128,
    )

    response = chat_completion.choices[0].message.content
    print("AI/ML API:\n", response)
    return response


def get_keywords_from_title(title):
    # Define the prompt for ChatGPT
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    prompt = (
        f"Extract relevant keywords from the following blog post title not english language words:\n\n"
        f"Title: {title}\n\n"
        f"Keywords:"
    )

    # prompt = (
    #             "Analyze the following blog post and suggest relevant topics and interests. "
    #             "Also, provide a summary of the content.\n\n"
    #             f"Blog Post:\n{title}\n\n"
    #             "Suggested Topics and Interests:\n"
    #             "Summary:"
    #         )
    try:
        # Create the chat completion request
        chat_completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",  # Replace with the appropriate model name
            messages=[
                {"role": "user", "content": prompt},  # User message
            ],
            temperature=0.5,  # Adjust as needed for creativity
            max_tokens=50,  # Adjust to get a suitable number of keywords
        )
        
        # Extract and return the keywords from the response
        keywords = chat_completion.choices[0].message.content.strip()
        return keywords
    except Exception as e:
        print("Exception: ", str(e))
        return None