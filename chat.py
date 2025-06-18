from openai import OpenAI
from db import save_chat_db, fetch_chat
import json

def ai_chat(user_id, input:str, chat_id):
    client = OpenAI()
    if chat_id:
        chat = fetch_chat(chat_id)
        print(chat)
        chat.append({"role": "user", "content": input})
    else:
        chat = []
        chat.append({"role": "user", "content": input})

    response = client.responses.create(
        model="gpt-4.1",
        input=chat
    )
    chat.append({"role": "assistant", "content": response.output_text})

    print(chat)
    c_id = save_chat_db(user_id, chat, chat_id)
    print(c_id)

    output = {"response" : response.output_text, "id": str(c_id)}
    return output



