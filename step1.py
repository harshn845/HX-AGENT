import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


client = OpenAI(
    base_url ="https://openrouter.ai/api/v1" , 
    api_key = os.getenv("NVIDIA_API_KEY")
)
messages = []

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ("exit" , "quit"):
        break

    messages.append({"role" : "user" ,"content" : user_input})

    response = client.chat.completions.create(
    model= os.getenv("MODEL_NAME"),
    messages = messages,
    )

    reply = response.choices[0].message.content
    messages.append({"role" : "assistant" , "content" : reply})
    print("bot:", reply)


    #USE THIS FOR CREATING A SIMPLE CHATBOT