from fastapi import HTTPException, UploadFile, APIRouter, Query, Body
from config import AUDIO_FILE_PATH
import os
from utils import process_audio_file
from db import save_transcript_db, get_transcripts_from_db, update_title_in_db, register_user, login_user, new_meeting, list_meeting, update_notification_settings, list_chats
from fastapi import UploadFile, File, Form
from pydantic import BaseModel, Json
from typing import Optional
from chat import ai_chat
from datetime import datetime
   
router = APIRouter()

@router.post("/upload-audio")
async def upload_audio_file(audio_file: UploadFile = Form(...), user_id:str = File(...), title:Optional[str] = Body(None)):
    try:
        # Check if audio_file is missing
        if audio_file is None:
            raise HTTPException(status_code=400, detail="Missing audio file parameter in the request")     
        generated_transcript, summary = process_audio_file(audio_file)
       
        await save_transcript_db(user_id, generated_transcript, summary, title)
        os.remove(AUDIO_FILE_PATH)
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
        result = await get_transcripts_from_db(user_id)
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
    return await update_title_in_db(id, update_title_request.new_title)

@router.post("/register-user")
async def create_new_user(
        user_id:str = Body(...),
        full_name:str = Body(...),
        job_title:str = Body(...),
        company_name:str = Body(...),
        password:str = Body(...),
        register_type = Body(...)
    ):
    return register_user(user_id, password, full_name, job_title, company_name, register_type)

@router.post("/login-user")
async def login_user(
        user_id:str = Body(...),
        password:str = Body(...),
    ):
    return login_user(user_id, password)

@router.post("/add-meeting")
async def add_new_meeting(
        user_id:str = Body(...),
        link:str = Body(...),
        title:str = Body(...),
        start_time:datetime = Body(...),
        end_time:datetime = Body(...),
    ):
    return new_meeting(user_id, link, start_time, end_time, title)


@router.get("/list-meetings")
async def list_meetings(
        user_id:str = Query(...)
    ):
    return list_meeting(user_id)

@router.put("/update-notification-settings")
async def update_settings(
        user_id:str = Body(...),
        setting_json:Json =  Body(...),
    ):
    return update_notification_settings(user_id, setting_json)

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
    return list_chats(user_id)