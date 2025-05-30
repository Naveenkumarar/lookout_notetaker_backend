from fastapi import HTTPException
from config import DB_NAME, MONGO_DB_URL, COLLECTION_NAME
from pymongo import MongoClient
from datetime import datetime
import json
from bson.json_util import dumps
from bson import ObjectId
from routes.types import User
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
    
    
def register_user(user_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db["user"]
        user = User(user_id=user_id)
        user_dict = user.model_dump()

        collection.insert_one(user_dict)
        print(f"User {user_id} registered successfully!")

        mongodb_client.close()
        return {"message" : "User registered successfully!"}
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

    