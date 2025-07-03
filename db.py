from hashlib import md5
from itertools import count
from fastapi import HTTPException
from pymongo.errors import BulkWriteError
from config import config
from pymongo import MongoClient
from datetime import datetime
import json,uuid
from bson.json_util import dumps
from bson import ObjectId
from models.Meeting import Meeting
from utils import get_audio_duration
from pymongo import DESCENDING
import base64
from fastapi import HTTPException, UploadFile
from models.User import ActionItems,ActionUpdate,RegisterUser
from typing import List

class DatabaseService:
    def __init__(self, ):
        self.mongodb_client = self.startup_db_client()
        self.db = self.mongodb_client[config.DB_NAME]
        self.collection = self.db[config.COLLECTION_NAME]
        self.action_collection=self.db[config.ACTION_COLLECTION_NAME]
        self.user_collection =self.db[config.USER_COLLECTION_NAME]
        self.meeting_collection=self.db[config.MEETING_COLLECTION_NAME]
        self.notification_setting_collection=self.db[config.NOTIFICATION_SETTING]
        self.conversation_collection=self.db[config.CONVERSATION]
        self.meeting_bot=self.db[config.MEETING_BOT]
        self.meeting_shares_collection=self.db[config.SHARED_COLLECTION]

    def startup_db_client(self):
        mongodb_client = MongoClient(config.MONGO_DB_URL)
        print("MongoDB client started successfully!")
        return mongodb_client

    async def save_transcript_db(self,user_id, transcript, summary, title):
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

        self.collection.insert_one(document)
        self.increment_user_notes_count(user_id)
        self.mongodb_client.close()
        print("Transcript saved to the db successfully!")


    async def get_transcripts_from_db(self,user_id: str):
        try:
            transcripts_cursor = self.collection.find({"user_id": user_id}).sort("created_at", DESCENDING)

            transcripts_list = list(transcripts_cursor)

            if not transcripts_list:
                raise HTTPException(status_code=404, detail=f"No transcripts found for user : {user_id}")
            self.mongodb_client.close()
            transcripts_json = json.loads(dumps(transcripts_list))
            return {"transcripts" : transcripts_json}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    async def update_title_in_db(self,user_id: str, new_title: str):
        try:
            _id = ObjectId(user_id)
            # Find the document matching the user_id and update the title
            result = self.collection.update_one(
                {"_id": _id},  # Query filter
                {"$set": {"title": new_title}}  # Update operation
            )
            self.mongodb_client.close()

            # Check if a document was modified
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=404, detail=f"No document found for user_id: {user_id}"
                )
            
            print(f"Meeting Title for user_id {user_id} updated successfully!")
            return {"message": f"Meeting Title updated successfully for user_id: {user_id}"}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    def register_user(self,user_id: str, password: str, full_name: str, job_title: str, company_name: str,profile_photo:str, register_type):
        try:
            existing_user = self.user_collection.find({"user_id": user_id})
            count = int(len(list(existing_user)))
            if count > 0:
                raise HTTPException(status_code=500, detail=f"failed to register user as email already exist")

            user = RegisterUser(
                user_id=user_id,
                notes_count=0,
                full_name=full_name,
                job_title=job_title or "",
                password=md5(password.encode()).hexdigest(),
                company_name=company_name or "",
                profile_photo= profile_photo or "" 
                
            )
            user_dict = user.model_dump()

            self.user_collection.insert_one(user_dict)
            print(f"User {user_id} registered successfully!")
            self.save_notification_settings(user_id)

            # self.mongodb_client.close()
            return json.loads(user.model_dump_json())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def login_user(self,user_id: str, password: str):
        user_cursor = self.user_collection.find_one({"user_id": user_id, "password": md5(password.encode()).hexdigest()})
        if user_cursor is None:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = dict(user_cursor)
        return user
    
    def get_user(self, user_id):
        user_cursor = self.user_collection.find_one({"user_id": user_id})
        user = dict(user_cursor)
        return user

    def increment_user_notes_count(self,user_id: str):
        try:           
            result = self.user_collection.update_one(
                {"user_id": user_id},  # Query filter to locate the user
                {"$inc": {"notes_count": 1}}  # Increment notes_count by 1
            )
            self.mongodb_client.close()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update notes count {str(e)}")

        
    def new_meeting(self, meetings: List[dict]):
        try:
            if not meetings:
                raise HTTPException(status_code=400, detail="No meetings provided.")
            result = self.meeting_collection.insert_many(meetings)
            for i in range(len(meetings)):
                meetings[i]['_id'] = str(result.inserted_ids[i]) 

            return {
                "message": "Meetings inserted successfully.",
                "inserted_count": len(result.inserted_ids),
                "status": "success",
                "data":meetings
            }

        except HTTPException:
            raise
        except BulkWriteError as bwe:
            raise HTTPException(status_code=500, detail=f"Bulk write error: {bwe.details}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to insert meetings: {str(e)}")





    def list_meeting(self,user_id: str):
        try:
            meeting_cursor = self.meeting_collection.find({"user_id": user_id})
            meeting = list(meeting_cursor)
            self.mongodb_client.close()
            meeting_json = json.loads(dumps(meeting))
            return {"meetings" : meeting_json}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to list meetings due to: {str(e)}")
        
    def save_notification_settings(self,user_id):

        notification = json.load(open('notification.json', 'r'))
        notification["user_id"] = user_id

        self.notification_setting_collection.insert_one(notification)
        self.mongodb_client.close()
        print("notification_settings saved to the db successfully!")

    def update_notification_settings(self,user_id, setting_json):

        print(setting_json)
        result = self.notification_setting_collection.update_many(
                {"user_id": user_id},  # Query filter to locate the user
                {"$set": setting_json}
            )

        cursor = self.notification_setting_collection.find({"user_id": user_id})
        setting = list(cursor)

        self.mongodb_client.close()
        setting_json = json.loads(dumps(setting))
        return {"setting" : setting_json}

    def fetch_chat(self,chat_id):

        _id = ObjectId(chat_id)
        cursor = self.conversation_collection.find({"_id": _id})
        chat = list(cursor)
        self.mongodb_client.close()
        chat_json = json.loads(dumps(chat))
        return chat_json[0].get('chat')


    def save_chat_db(self,user_id, chat, chat_id):
        if chat_id:
            _id = ObjectId(chat_id)
            self.conversation_collection.update_one(
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

            result = self.conversation_collection.insert_one(document)

        self.mongodb_client.close()
        print("Chat saved to the db successfully!")
        if chat_id:
            return chat_id
        else:
            return result.inserted_id

    def list_chats(self,user_id: str):
        try:
            chat_cursor = self.conversation_collection.find({"user_id": user_id})
            chat = list(chat_cursor)
            self.mongodb_client.close()
            chat_json = json.loads(dumps(chat))
            return {"chats" : chat_json}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to list chat due to: {str(e)}")  
        
    def create_bot_record(self,user_id: str, resp, meeting_id):
        try:
            print('**********')
            print(resp.get('id'))
            document = {
                "user_id": user_id,
                "bot_id": resp.get('id'),
                "created_at": datetime.now(),
                "meeting_id": meeting_id
            }

            result = self.meeting_bot.insert_one(document)

            self.mongodb_client.close()
            output = {"bot_id" : resp.get('id'), "id": str(result.inserted_id)}
            return output
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to list chat due to: {str(e)}")
        

    def list_bots(self,user_id: str):
        try:
            bot_cursor = self.meeting_bot.find({"user_id": user_id})
            bot = list(bot_cursor)
            self.mongodb_client.close()
            bot_json = json.loads(dumps(bot))
            return {"bots" : bot_json}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to list bots due to: {str(e)}")

    async def add_action_items(self,note_id: str,user_id: str, action_items: ActionItems):
        try:
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

            result =  self.action_collection.update_one(
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

    async def get_action_items(self,note_id,user_id):
        try:
            response=list(self.action_collection.find({"note_id":note_id,"user_id":user_id},{"_id":0,"actions":1}))
            return {
                "message": f"Fetched action items successfully for note_id: {note_id}",
                "status": "success",
                "data":response
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get action items: {str(e)}")
        
    async def update_action_item(self,note_id: str, user_id: str, action: ActionUpdate):
        try:
            result =  self.action_collection.update_one(
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




    def save_meeting_notes(self,user_id: str, meeting_id: str, notes: str):
        try:
            _id = ObjectId(user_id)
            note_id = str(uuid.uuid4())

            new_note = {
                "note_id": note_id,
                "notes": notes,
                "note_timestamp": datetime.now()
            }

            # Push the new note into the notes array of the document that matches _id and meeting_id
            result = self.collection.update_one(
                {"_id": _id, "meeting_id": meeting_id},
                {"$push": {"notes": new_note}}
            )

            self.mongodb_client.close()

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Meeting not found for the user")

            return {"message": f"Note added for user_id: {user_id} with meeting_id: {meeting_id}","status":"success"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))



    def edit_meeting_notes(self,user_id: str, meeting_id: str, note_id: str, notes: str):
        
        try:
            _id = ObjectId(user_id)
            new_notes_text = notes
            print("DEBUG:")
            print("user_id (ObjectId):", _id)
            print("meeting_id:", repr(meeting_id))
            print("note_id:", repr(note_id))

            # Debug: Check whether the note exists first
            existing = self.collection.find_one({
                "_id": _id,
                "meeting_id": meeting_id,
                "notes.note_id": note_id
            })

            if not existing:
                raise HTTPException(status_code=404, detail="Note not found for the given user and meeting")

            # Perform the update
            result = self.collection.update_one(
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

            self.mongodb_client.close()

            return {"message": f"Note with note_id '{note_id}' successfully updated.","status":"success"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def get_meeting_notes(self,user_id: str, meeting_id: str):
        try:
            _id = ObjectId(user_id)
            meeting_id = meeting_id.strip()

            # Find the document with matching user_id and meeting_id
            result = self.collection.find_one({
                "_id": _id,
                "meeting_id": meeting_id
            }, {
                "notes": 1, "_id": 0 
            })

            self.mongodb_client.close()
            print("resulttt",result)

            if not result:
                raise HTTPException(status_code=404, detail="Meeting notes not found.")

            return {"notes": result.get("notes", [])}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        





    def save_comments(self,user_id: str, meeting_id: str, comments: str):
        try: 
            _id = ObjectId(user_id)
            comment_id = str(uuid.uuid4())

            new_comment = {
                "comment_id": comment_id,
                "comments": comments,
                "comment_timestamp": datetime.now()
            }

            # Push the new comment into the comments array of the document that matches _id and meeting_id
            result = self.collection.update_one(
                {"_id": _id, "meeting_id": meeting_id},
                {"$push": {"comments": new_comment}}
            )

            self.mongodb_client.close()

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Meeting not found for the user")

            return {"message": f"Comment added for user_id: {user_id} with meeting_id: {meeting_id}","status":"success"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_comments(self,user_id: str, meeting_id: str):
        try:
            _id = ObjectId(user_id)
            meeting_id = meeting_id.strip()

            # Find the document with matching user_id and meeting_id
            result = self.collection.find_one({
                "_id": _id,
                "meeting_id": meeting_id
            }, {
                "comments": 1, "_id": 0 
            })

            self.mongodb_client.close()
            print("resulttt",result)

            if not result:
                raise HTTPException(status_code=404, detail="Meeting Comments not found.")

            return {"comments": result.get("comments", [])}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    def update_profile_details(self,user_id,update_data):
        try:
            if not update_data:
                raise HTTPException(status_code=400, detail="No valid fields to update.")

            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found.")

            return {"message": "User updated successfully", "updated_fields": list(update_data.keys())}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def update_password_details(self, user_id: str, old_password: str, new_password: str):
        try:
            hashed_old_password = md5(old_password.encode()).hexdigest()

            user = self.collection.find_one({"user_id": user_id})
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            if user["password"] != hashed_old_password:
                raise HTTPException(status_code=401, detail="Old password is incorrect.")

            # Hash the new password
            hashed_new_password = md5(new_password.encode()).hexdigest()

            # Update the password
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"password": hashed_new_password}}
            )

            return {"message": "Password updated successfully."}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def add_profile_photo(self, user_id: str, profile_photo: UploadFile):
        try:
            # Read file content
            file_content = profile_photo.file.read()
            encoded_string = base64.b64encode(file_content).decode("utf-8")

            # Update in DB
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"profile_photo": encoded_string}}
            )

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found.")

            return {
                "message": "Profile photo updated successfully",
                "filename": profile_photo.filename
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def save_meeting_share(self,sender_id: str, receiver_id: str, meeting_id: str):
        share_data = {
            "sender_id": sender_id,
            "receiver_addr": receiver_id,
            "meeting_id": meeting_id,
            "shared_time": datetime.utcnow()
        }
        result=self.meeting_shares_collection.insert_one(share_data)
        if result:
            return True
        return False

    
    async def verify_all_recipients_exist(self, recipients: list[str]) -> list[str]:
        """Check if all recipients exist in the DB. Return list of missing emails."""
        cursor = self.user_collection.find({"user_id": {"$in": recipients}})
        existing_users = [doc["user_id"] for doc in cursor] 
        missing = [r for r in recipients if r not in existing_users]
        return missing



        