from fastapi import HTTPException, UploadFile, APIRouter, Query, Body
from config import config
import os
from push_notifications import send_test_notification
from utils import process_audio_file
from fastapi import UploadFile, File, Form, Depends
from pydantic import BaseModel, Json
from typing import Annotated, Optional, Union
from models.User import ActionItems,ActionUpdate,AddNote,AddComment,RegisterUser, User,UserUpdate,PasswordUpdateRequest
from chat import ai_chat
from meeting_bot import createbot, botstatus, getrecording, transcript
from datetime import datetime
from emails import send_email_invite,share_email_invite
from typing import List
from fastapi.responses import HTMLResponse
from jwt_auth import get_access_token, get_current_user
from push_notifications import send_test_notification
   
router = APIRouter()
from db import DatabaseService
db_service=DatabaseService()

@router.post("/upload-audio")
async def upload_audio_file(audio_file: UploadFile = Form(...), user_id:str = File(...), title:Optional[str] = Body(None)):
    try:
        # Check if audio_file is missing
        if audio_file is None:
            raise HTTPException(status_code=400, detail="Missing audio file parameter in the request")     
        generated_transcript, summary = process_audio_file(audio_file)
       
        await db_service.save_transcript_db(user_id, generated_transcript, summary, title)
        os.remove(config.AUDIO_FILE_PATH)
        print("audio file deleted //////////////////")
        return {
            "status": "Transcript generated successfully!",
            "transcript": generated_transcript,
            "summary": summary,
            "code": 200
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.get("/transcripts/", response_model=None)
async def get_transcripts_for_user(user_id: str = Query(...)):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        result = await db_service.get_transcripts_from_db(user_id)
        return result
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    

class UpdateTitleRequest(BaseModel):
    new_title: str

@router.put("/update-meeting-title")
async def update_meeting_title(
    id: str = Query(...),
    update_title_request: UpdateTitleRequest = Body(...)
):
    return await db_service.update_title_in_db(id, update_title_request.new_title)

# @router.post("/register-user")
# async def create_new_user(user_id:str = Body(...)):
#     return register_user(user_id)

@router.post("/register-user")
async def register_new_user(user: RegisterUser):
    return db_service.register_user(user.user_id,user.password,user.full_name,user.job_title,user.company_name,user.profile_photo,user.register_type)


@router.post("/add-action-items")
async def add_action(
    note_id: str = Query(...),
    user_id:str = Query(...),
    add_items_request: ActionItems = Body(...)
):
    return await db_service.add_action_items(note_id,user_id, add_items_request)



@router.get("/list-action-items")
async def get_actions(
    note_id: str = Query(...),
    user_id:str = Query(...)
):
    return await db_service.get_action_items(note_id, user_id)


@router.put("/mark-action-items")
async def mark_actions(
    note_id: str = Query(...),
    user_id:str = Query(...),
    action_items: ActionUpdate = Body(...)
):
    return await db_service.update_action_item(note_id, user_id,action_items)



@router.post("/save-meeting-notes")
async def add_meeting_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...),
    note_items: AddNote = Body(...)
):
    try:
        result =  db_service.save_meeting_notes(user_id, meeting_id, note_items.notes)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    
@router.post("/add-comments")
async def add_comments(
    user_id: str = Query(...),
    meeting_id: str = Query(...),
    comments:  AddComment= Body(...)
):
    try:
        result =  db_service.save_comments(user_id, meeting_id, comments.comment)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")

@router.post("/edit-meeting-notes")
async def edits_meeting_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...),
    note_id:str = Query(...),
    note_items: AddNote = Body(...)
):
    try:
        result =  db_service.edit_meeting_notes(user_id, meeting_id, note_id,note_items.notes)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    


@router.get("/get-meeting-notes")
async def get_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...)
):
    try:
        result =  db_service.get_meeting_notes(user_id, meeting_id)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    

@router.get("/get-comments")
async def get_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...)
):
    try:
        result =  db_service.get_comments(user_id, meeting_id)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    
async def create_new_user(
        user_id:str = Body(...),
        full_name:str = Body(...),
        job_title:str = Body(...),
        company_name:str = Body(...),
        password:str = Body(...),
        register_type = Body(...),
        profile_photo:str=Body(...)
    ):
    return db_service.register_user(user_id, password, full_name, job_title, company_name,profile_photo, register_type)

@router.post("/login-user")
async def login_user(
        user_id:str = Body(...),
        password:str = Body(...),
    ):
    send_test_notification('arnask')
    return get_access_token(user_id, password)

@router.post("/add-meeting")
async def add_new_meeting(
        user_id:str = Body(...),
        link:str = Body(...),
        title:str = Body(...),
        start_time:datetime = Body(...),
        end_time:datetime = Body(...),
    ):
    return db_service.new_meeting(user_id, link, start_time, end_time, title)


@router.get("/list-meetings")
async def list_meetings(
        current_user: Annotated[User, Depends(get_current_user)],
        user_id:str = Query(...),
    ):
    return db_service.list_meeting(user_id)

@router.put("/update-notification-settings")
async def update_settings(
        user_id:str = Body(...),
        setting_json:Json =  Body(...),
    ):
    return db_service.update_notification_settings(user_id, setting_json)

@router.post("/chat")
async def ai_chatting(
        user_id:str = Body(...),
        chat_input:str = Body(...),
        chat_id:Optional[str] = Body(None)
    ):
    print(chat_input)
    return ai_chat(user_id, chat_input, chat_id)

@router.get("/list-chats")
async def chat_list(
        user_id:str = Query(...)
    ):
    return db_service.list_chats(user_id)


@router.post("/create-bot")
async def meeting_bot(
        user_id:str = Body(...),
        meeting_id:Optional[str] = Body(None),
        meeting_url:str = Body(...)
    ):
    return createbot(user_id, meeting_url, meeting_id)

@router.get("/list-bots")
async def bot_list(
        user_id:str = Query(...)
    ):
    return db_service.list_bots(user_id)

@router.get("/bot-status")
async def bot_status(
        bot_id:str = Query(...)
    ):
    return botstatus(bot_id)

@router.get("/transcript")
async def get_transcript(
        bot_id:str = Query(...)
    ):
    return transcript(bot_id)

@router.get("/get-recording")
async def bot_list(
        bot_id:str = Query(...)
    ):
    return getrecording(bot_id)



@router.put("/update-profile/{user_id}")
async def update_user(user_id: str, updates: UserUpdate):
    update_data = updates.dict(exclude_unset=True)
    return db_service.update_profile_details(user_id,update_data)

@router.put("/update-profile-password/{user_id}")
async def update_password(user_id: str, payload: PasswordUpdateRequest):
    return db_service.update_password_details(
        user_id=user_id,
        old_password=payload.old_password,
        new_password=payload.new_password
    )

@router.post("/add-profile-pic/{user_id}")
async def add_pic(user_id: str, profile_photo: UploadFile = File(...)):
    return db_service.add_profile_photo(user_id, profile_photo)

@router.post("/send-invite")
async def send_invite(
        user_id:str = Body(...),
        recipients_addr:Json = Body(...)
    ):
    send_test_notification(user_id)
    return send_email_invite(recipients_addr, user_id)

@router.post("/share")
async def share(
    sender_id: str = Body(...),
    meeting_id: str = Body(...),
    recipients_addr: List[str] = Body(...)
):
    
    receiver = await db_service.verify_all_recipients_exist(recipients_addr)
    print("step1 done")
    if receiver:
        raise HTTPException(status_code=404,detail= f"These recipients are missing: {', '.join(receiver)}")
    try:
        await db_service.save_meeting_share(sender_id, recipients_addr, meeting_id)
        print("stored")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save share: {str(e)}")

    try:
        print("sending email")
        share_email_invite(recipients_addr, sender_id,meeting_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Meeting shared successfully","status":"success"}

@router.get("/join-meeting", response_class=HTMLResponse)
async def join_meeting_form():
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Join Meeting</title>
    </head>
    <body>
      <h2>Enter Your Meeting ID</h2>
      <form action="/go-to-meeting" method="get">
        <input type="text" name="meeting_id" placeholder="Enter meeting ID" required>
        <button type="submit">Join</button>
      </form>
    </body>
    </html>
    """

from fastapi.security import HTTPBearer
from models.User import User
from verify_token import verify_token

bearer_scheme = HTTPBearer()

class UserRegister(BaseModel):
    company: Optional[str] = None
    name: Optional[str] = None
    job_title: Optional[str] = None
    credit: Optional[int] = 100


@router.post("/register")
async def register_user(user: UserRegister = Body(...),
                        token: str = Depends(bearer_scheme)
                        ):
    token_validation = verify_token(token)
    if(token_validation["status"]):
        email = token_validation['decoded_token']['email']
        try:
            new_user = User(
                email=email,
                company=user.company,
                name=user.name,
                job_title=user.job_title,
            )
            json_user = await db_service.register_new_user(new_user)
            return {
                "status_code": 200,
                "response_type": "success",
                "description": "User Created successfully",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")
    raise HTTPException(status_code=403, detail="Invalid Token")

@router.get("/login")
async def get_user(token: str = Depends(bearer_scheme)):
    token_validation = verify_token(token)
    if(token_validation["status"]):
        try:
            email = token_validation['decoded_token']['email']
            user = await db_service.login_new_user(email)
            
            return {
                "status_code": 200,
                "response_type": "success",
                "description": "Login successfully",
                "data": user,
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to login user: {str(e)}")
    raise HTTPException(status_code=403, detail="Invalid Token")

