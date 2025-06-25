from openai import OpenAI
from db import DatabaseService
import json

db_service=DatabaseService()

def ai_chat(user_id, input:str, chat_id):
    client = OpenAI()
    if chat_id:
        chat = db_service.fetch_chat(chat_id)
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
    c_id = db_service.save_chat_db(user_id, chat, chat_id)
    print(c_id)

    output = {"response" : response.output_text, "id": str(c_id)}
    return output



