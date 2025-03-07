# import openai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# system_content = "You are a travel agent. Be descriptive and helpful."
# user_content = "Suggest the topic for blogging on IT"

# client = openai.OpenAI(
#     api_key=os.getenv('OPENAI_KEY'),
#     base_url="https://api.aimlapi.com",
# )

# chat_completion = client.chat.completions.create(
#     model="mistralai/Mistral-7B-Instruct-v0.2",
#     messages=[
#         # {"role": "system", "content": system_content},
#         {"role": "user", "content": user_content},
#     ],
#     temperature=0.7,
#     max_tokens=128,
# )

# response = chat_completion.choices[0].message.content
# print("AI/ML API:\n", response)
