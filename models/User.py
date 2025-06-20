from pydantic import BaseModel
from typing import Optional,List,Dict,Any
from pydantic import (BaseModel, SecretStr)
from typing import Optional
from enum import Enum

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


class RegisterTypeEnum(str, Enum):
    app = 'app'
    social = 'social'

class User(BaseModel):
   user_id:str
   notes_count:int
   full_name:str
   job_title:str
   company_name:str
   password: Optional[str]
   register_type: RegisterTypeEnum = RegisterTypeEnum.app
