from django.utils import timezone
from django.conf import settings
import cloudinary
import cloudinary.api
import cloudinary.uploader
import os
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .models import User

import pyotp
import qrcode
from io import BytesIO
from django.core.files import File
import re
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
    

def chatgpt_engine(title):
    # system_content = "You are a travel agent. Be descriptive and helpful."
    # user_content = "Suggest the topic for blogging on IT"

    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    prompt = (
        f"Provide the content of following title of blog post please keep in short:\n\n"
        f"Title: {title}\n\n"
    )
    try:
        chat_completion = client.chat.completions.create(
            # model="mistralai/Mistral-7B-Instruct-v0.2",
            model = 'gpt-4o',
            messages=[
                # {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
            ],
            # prompt = user_content,
            temperature=0.7,
            max_tokens=50,
        )

        response = chat_completion.choices[0].message.content.strip().split('\n\n')
        print("AI/ML API:\n", response)
        return response
    except Exception as e:
        print("Exception: ", str(e))
        return None


def get_keywords_from_title(title, content):
    # Define the prompt for ChatGPT
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    # prompt = (
    #     f"Extract relevant keywords from the following blog post title not general used english language words:\n\n"
    #     f"Title: {text}\n\n"
    #     f"Keywords:"
    # )

    # prompt = (
    #     "Analyze the following text and provide insights:\n\n"
    #     f"Text: {text}\n\n"
    #     "Insights:"
    # )

    prompt = (
        "Analyze the following blog post and extract interesting topics:\n\n"
        f"Title: {title}\n\n"
        f"Content: {content}\n\n"
        "Extracted Topics:"
    )

    # prompt = (
    #             "Analyze the following blog post and suggest relevant topics and interests. "
    #             "Also, provide a summary of the content.\n\n"
    #             f"Blog Post:\n{text}\n\n"
    #             "Suggested Topics and Interests:\n"
    #             "Summary:"
    #         )
    try:
        # Create the chat completion request
        chat_completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",  # Replace with the appropriate model name
            # model = "gpt-4",
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
    
def remove_leading_numeric_chars(s):
    return re.sub(r'^\d.+', '', s)

def remove_leading_numbers_and_special_chars(s):
    # Regex pattern to match leading numbers and special characters
    return re.sub(r'^[\d\W_]+', '', s)

def extract_topics_from_post(title, content):
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )
    prompt = (
        "Analyze the following blog post and extract top 5 interesting topics:\n\n"
        f"Title: {title}\n\n"
        f"Content: {content}\n\n"
        "Extracted Topics:"
    )

    try:
        # Create the chat completion request
        response = client.chat.completions.create(
            # model="mistralai/Mistral-7B-Instruct-v0.2",
            model = "gpt-4",
            messages=[
                {"role": "user", "content": prompt},  # User message
            ],
            temperature=0.5,  # Adjust as needed for creativity
            max_tokens=30,  # Adjust to get a suitable number of keywords
        )
        
        # Extract and return the keywords from the response
        topics = response.choices[0].message.content.strip()
        topics_list = topics.split('\n')
        print("topic list: ", topics_list)
        updated_list = []
        for topic in topics_list:
            print("topic:", topic)
            if topic != '':
                topic = topic.split(':')[0].replace('*', '')
                topic = remove_leading_numbers_and_special_chars(topic)
                updated_list.append(topic.strip())
        return updated_list

    except Exception as e:
        print("Exception: ", str(e))
        return None
    

def generate_topic_suggestions(tags):
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    prompt = (
        "Based on the following tags, suggest new related topic for a blog post: "
        f"{', '.join(tags)}. Provide a list of 5 new topic not details."
    )

    # Call GPT-4 API
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # You can use "gpt-4" or other available models
            messages=[
                {"role": "user", "content": prompt},  # User message
            ],
            
            max_tokens=30,
            temperature=0.7
        )

        # Parse the response
        print(response)
        suggestions = response.choices[0].message.content.strip().split('\n')
        print("suggestion topic : ", suggestions)
        return [tag.strip() for tag in suggestions if tag.strip()]
    except Exception as e:
        print("Exception: ", str(e))
        return None


## Tags suggestion done 
def generate_tag_suggestions(existing_tags):
    # Construct the prompt for GPT
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_KEY'),
        base_url="https://api.aimlapi.com",
    )

    prompt = (
        "Based on the following tags, suggest new related tags for a blog post: "
        f"{', '.join(existing_tags)}. Provide a list of 5 new tags not details."
    )

    # Call GPT-4 API
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # You can use "gpt-4" or other available models
            messages=[
                {"role": "user", "content": prompt},  # User message
            ],
            
            max_tokens=30,
            temperature=0.7
        )

        # Parse the response
        print(response)
        suggestions = response.choices[0].message.content.strip().split('\n')
        print("suggestion tags : ", suggestions)
        return [tag.strip() for tag in suggestions if tag.strip()]
    except Exception as e:
        print("Exception: ", str(e))
        return None



### auto content suggestion based on title.
### auto title and topic to write based on its previous created blog and 


def generate_otp_secret():
    return pyotp.random_base6()

def generate_qr_code(otp_secret, user_email):
    totp = pyotp.TOTP(otp_secret)
    otp_uri = totp.provisioning_uri(name=user_email, issuer_name="YourAppName")
    
    qr = qrcode.make(otp_uri)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    
    return File(buffer, name='qr_code.png')