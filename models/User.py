from pydantic import (BaseModel, SecretStr)
from typing import Optional
from enum import Enum

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
