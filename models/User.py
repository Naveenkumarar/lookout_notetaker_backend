from pydantic import BaseModel
from typing import Optional,List,Dict,Any

class User(BaseModel):
   user_id:str

class ActionItems(BaseModel):
   note: Optional[str] = None
   actions: List[Dict[str, Any]]

class ActionList(BaseModel):
   actions: List[Dict[str, Any]]

class ActionUpdate(BaseModel):
    task: str
    status: str

class AddNote(BaseModel):
   notes:str
