from fastapi import HTTPException, UploadFile, APIRouter, Query, Body
from config import AUDIO_FILE_PATH
import os
from utils import process_audio_file
from db import save_transcript_db, get_transcripts_from_db, update_title_in_db, register_user
from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from routes.types import User
   
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
async def create_new_user(user_id:str = Body(...)):
    return register_user(user_id)
