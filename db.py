from hashlib import md5
from fastapi import HTTPException
from config import DB_NAME, MONGO_DB_URL, COLLECTION_NAME,ACTION_COLLECTION_NAME
from pymongo import MongoClient
from datetime import datetime
import json,uuid
from bson.json_util import dumps
from bson import ObjectId
from models.User import User
from models.Meeting import Meeting
from utils import get_audio_duration
from pymongo import DESCENDING
from models.User import ActionItems,ActionUpdate


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

async def add_action_items(note_id: str,user_id: str, action_items: ActionItems):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        action_collection = db[ACTION_COLLECTION_NAME]

        # Filter document by note_id and user id    ## check with prod team
        filter_query = {
            "note_id": note_id,
            "user_id": user_id
        }

        update_data = {
            "$setOnInsert": {
                "note": action_items.note,
                "note_id": note_id,
                "user_id": user_id,
                
            },
            "$push": {
                "actions": {
                    "$each": action_items.actions
                }
            }
        }

        result =  action_collection.update_one(
            filter_query,
            update_data,
            upsert=True
        )

        return {
            "message": f"Action items added/updated successfully for note_id: {note_id}",
            "status": "success",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add or update action items: {str(e)}")

async def get_action_items(note_id,user_id):
    try:

        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        action_collection = db[ACTION_COLLECTION_NAME]
        response=list(action_collection.find({"note_id":note_id,"user_id":user_id},{"_id":0,"actions":1}))
        return {
            "message": f"Fetched action items successfully for note_id: {note_id}",
            "status": "success",
            "data":response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get action items: {str(e)}")
    
async def update_action_item(note_id: str, user_id: str, action: ActionUpdate):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        action_collection = db[ACTION_COLLECTION_NAME]

        result =  action_collection.update_one(
            {
                "note_id": note_id,
                "user_id": user_id,
                "actions.task": action.task  
            },
            {
                "$set": {
                    "actions.$.status": action.status
                }
            }
        )

        return {
            "message": f"Task '{action.task}' updated to status '{action.status}'",
            "status":"success",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update action items: {str(e)}")




def save_meeting_notes(user_id: str, meeting_id: str, notes: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db[COLLECTION_NAME]

        _id = ObjectId(user_id)
        note_id = str(uuid.uuid4())

        new_note = {
            "note_id": note_id,
            "notes": notes,
            "note_timestamp": datetime.now()
        }

        # Push the new note into the notes array of the document that matches _id and meeting_id
        result = collection.update_one(
            {"_id": _id, "meeting_id": meeting_id},
            {"$push": {"notes": new_note}}
        )

        mongodb_client.close()

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Meeting not found for the user")

        return {"message": f"Note added for user_id: {user_id} with meeting_id: {meeting_id}","status":"success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def edit_meeting_notes(user_id: str, meeting_id: str, note_id: str, notes: str):
    
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db[COLLECTION_NAME]

        _id = ObjectId(user_id)
        new_notes_text = notes
        print("DEBUG:")
        print("user_id (ObjectId):", _id)
        print("meeting_id:", repr(meeting_id))
        print("note_id:", repr(note_id))

        # Debug: Check whether the note exists first
        existing = collection.find_one({
            "_id": _id,
            "meeting_id": meeting_id,
            "notes.note_id": note_id
        })

        if not existing:
            raise HTTPException(status_code=404, detail="Note not found for the given user and meeting")

        # Perform the update
        result = collection.update_one(
            {
                "_id": _id,
                "meeting_id": meeting_id,
                "notes.note_id": note_id
            },
            {
                "$set": {
                    "notes.$.notes": new_notes_text,
                    "notes.$.note_timestamp": datetime.now()
                }
            }
        )

        mongodb_client.close()

        return {"message": f"Note with note_id '{note_id}' successfully updated.","status":"success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_meeting_notes(user_id: str, meeting_id: str):
    try:
        mongodb_client = startup_db_client()
        db = mongodb_client[DB_NAME]
        collection = db[COLLECTION_NAME]

        _id = ObjectId(user_id)
        meeting_id = meeting_id.strip()

        # Find the document with matching user_id and meeting_id
        result = collection.find_one({
            "_id": _id,
            "meeting_id": meeting_id
        }, {
            "notes": 1, "_id": 0 
        })

        mongodb_client.close()
        print("resulttt",result)

        if not result:
            raise HTTPException(status_code=404, detail="Meeting notes not found.")

        return {"notes": result.get("notes", [])}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
