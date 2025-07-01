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

class AddComment(BaseModel):
   comment:str



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

class RegisterUser(BaseModel):
   user_id:str
   full_name:str
   job_title: Optional[str] = None
   company_name: Optional[str] = None
   password: str
   register_type: RegisterTypeEnum = RegisterTypeEnum.app
   profile_photo:str = ""

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str


