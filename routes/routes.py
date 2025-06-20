from fastapi import HTTPException, UploadFile, APIRouter, Query, Body
from config import AUDIO_FILE_PATH
import os
from utils import process_audio_file
from db import save_transcript_db, get_transcripts_from_db, update_title_in_db, register_user,add_action_items,get_action_items,update_action_item,save_meeting_notes,edit_meeting_notes,get_meeting_notes
from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from routes.types import User
from models.User import ActionItems,ActionUpdate,AddNote
   
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


@router.post("/add-action-items")
async def add_action(
    note_id: str = Query(...),
    user_id:str = Query(...),
    add_items_request: ActionItems = Body(...)
):
    return await add_action_items(note_id,user_id, add_items_request)



@router.get("/list-action-items")
async def get_actions(
    note_id: str = Query(...),
    user_id:str = Query(...)
):
    return await get_action_items(note_id, user_id)


@router.put("/mark-action-items")
async def mark_actions(
    note_id: str = Query(...),
    user_id:str = Query(...),
    action_items: ActionUpdate = Body(...)
):
    return await update_action_item(note_id, user_id,action_items)



@router.post("/save-meeting-notes")
async def add_meeting_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...),
    note_items: AddNote = Body(...)
):
    try:
        result =  save_meeting_notes(user_id, meeting_id, note_items.notes)
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
        result =  edit_meeting_notes(user_id, meeting_id, note_id,note_items.notes)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")
    


@router.get("/get-meeting-notes")
async def get_notes(
    user_id: str = Query(...),
    meeting_id: str = Query(...)
):
    try:
        result =  get_meeting_notes(user_id, meeting_id)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Value error")