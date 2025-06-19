from hashlib import md5
from fastapi import HTTPException
from config import DB_NAME, MONGO_DB_URL, COLLECTION_NAME
from pymongo import MongoClient
from datetime import datetime
import json
from bson.json_util import dumps
from bson import ObjectId
from models.User import User
from models.Meeting import Meeting
from utils import get_audio_duration
from pymongo import DESCENDING


def startup_db_client():
    mongodb_client = MongoClient(MONGO_DB_URL)
    print("MongoDB client started successfully!")
    return mongodb_client

async def save_transcript_db(user_id, transcript, summary, title):
    mongodb_client = startup_db_client()
    db = mongodb_client[DB_NAME]
    collection = db[COLLECTION_NAME]
    duration = get_audio_duration()
    # duration= ":02:01:33"
    document = {
        "user_id": user_id,
        "transcript": transcript,
        "summary": summary,
        "created_at": datetime.now(),
        "title": title,
        "duration": duration
    }

    collection.insert_one(document)
    increment_user_notes_count(user_id)
    mongodb_client.close()
    print("Transcript saved to the db successfully!")


async def get_transcripts_from_db(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        transcripts_cursor = collection.find({"user_id": user_id}).sort("created_at", DESCENDING)

        transcripts_list = list(transcripts_cursor)

        if not transcripts_list:
            raise HTTPException(status_code=404, detail=f"No transcripts found for user : {user_id}")
        mongodb_client.close()
        transcripts_json = json.loads(dumps(transcripts_list))
        return {"transcripts" : transcripts_json}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def update_title_in_db(user_id: str, new_title: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        _id = ObjectId(user_id)
        # Find the document matching the user_id and update the title
        result = collection.update_one(
            {"_id": _id},  # Query filter
            {"$set": {"title": new_title}}  # Update operation
        )
        mongodb_client.close()

        # Check if a document was modified
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404, detail=f"No document found for user_id: {user_id}"
            )
        
        print(f"Meeting Title for user_id {user_id} updated successfully!")
        return {"message": f"Meeting Title updated successfully for user_id: {user_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def register_user(user_id: str, password: str, full_name: str, job_title: str, company_name: str, register_type):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["user"]
        user = User(
            user_id=user_id,
            notes_count=0,
            full_name=full_name,
            job_title=job_title,
            password=md5(password.encode()).hexdigest(),
            company_name=company_name
        )
        user_dict = user.model_dump()

        collection.insert_one(user_dict)
        print(f"User {user_id} registered successfully!")
        save_notification_settings(user_id)

        mongodb_client.close()
        return json.loads(user.model_dump_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to register user due to: {str(e)}")

def login_user(user_id: str, password: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["user"]
        user_cursor = collection.find({"user_id": user_id, "password": md5(password.encode()).hexdigest()})

        user = list(user_cursor)

        mongodb_client.close()
        user_json = json.loads(dumps(user))
        return {"user" : user_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to register user due to: {str(e)}")

def increment_user_notes_count(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["user"]
        
        result = collection.update_one(
            {"user_id": user_id},  # Query filter to locate the user
            {"$inc": {"notes_count": 1}}  # Increment notes_count by 1
        )
        mongodb_client.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notes count {str(e)}")
    

def new_meeting(user_id: str, link: str, start_time: str, end_time: str, title: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["meeting"]
        meeting = Meeting(
            user_id=user_id,
            link=link,
            start_time=start_time,
            end_time=end_time,
            title=title
        )
        meeting_dict = meeting.model_dump()

        collection.insert_one(meeting_dict)
        print(f"Meeting created successfully!")

        mongodb_client.close()
        return json.loads(meeting.model_dump_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to create meeting due to: {str(e)}")

def list_meeting(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["meeting"]
        meeting_cursor = collection.find({"user_id": user_id})

        meeting = list(meeting_cursor)

        mongodb_client.close()
        meeting_json = json.loads(dumps(meeting))
        return {"meetings" : meeting_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to list meetings due to: {str(e)}")
    
def save_notification_settings(user_id):
    mongodb_client = startup_db_client()
    db = mongodb_client[DB_NAME]
    collection = db['notification_setting']

    notification = json.load(open('notification.json', 'r'))
    notification["user_id"] = user_id

    collection.insert_one(notification)
    mongodb_client.close()
    print("notification_settings saved to the db successfully!")

def update_notification_settings(user_id, setting_json):
    mongodb_client = startup_db_client()
    db = mongodb_client[DB_NAME]
    collection = db['notification_setting']

    print(setting_json)
    result = collection.update_many(
            {"user_id": user_id},  # Query filter to locate the user
            {"$set": setting_json}
        )

    cursor = collection.find({"user_id": user_id})
    setting = list(cursor)

    mongodb_client.close()
    setting_json = json.loads(dumps(setting))
    return {"setting" : setting_json}

def fetch_chat(chat_id):
    mongodb_client = startup_db_client()
    db = mongodb_client[DB_NAME]
    collection = db['conversation']
    _id = ObjectId(chat_id)
    cursor = collection.find({"_id": _id})
    chat = list(cursor)

    mongodb_client.close()
    chat_json = json.loads(dumps(chat))
    return chat_json[0].get('chat')


def save_chat_db(user_id, chat, chat_id):
    mongodb_client = startup_db_client()
    db = mongodb_client[DB_NAME]
    collection = db['conversation']
    if chat_id:
        _id = ObjectId(chat_id)
        collection.update_one(
            {"_id": _id},  # Query filter to locate the user
            {"$set": {"chat": chat}}
        )
    else:
        document = {
            "user_id": user_id,
            "chat": chat,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = collection.insert_one(document)

    mongodb_client.close()
    print("Chat saved to the db successfully!")
    if chat_id:
        return chat_id
    else:
        return result.inserted_id

def list_chats(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["conversation"]
        chat_cursor = collection.find({"user_id": user_id})

        chat = list(chat_cursor)

        mongodb_client.close()
        chat_json = json.loads(dumps(chat))
        return {"chats" : chat_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to list chat due to: {str(e)}")  
    
def create_bot_record(user_id: str, resp, meeting_id):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["meeting_bot"]
        print('**********')
        print(resp.get('id'))
        document = {
            "user_id": user_id,
            "bot_id": resp.get('id'),
            "created_at": datetime.now(),
            "meeting_id": meeting_id
        }

        result = collection.insert_one(document)

        mongodb_client.close()
        output = {"bot_id" : resp.get('id'), "id": str(result.inserted_id)}
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to list chat due to: {str(e)}")
    

def list_bots(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["meeting_bot"]
        bot_cursor = collection.find({"user_id": user_id})

        bot = list(bot_cursor)

        mongodb_client.close()
        bot_json = json.loads(dumps(bot))
        return {"bots" : bot_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to list bots due to: {str(e)}")