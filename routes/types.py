from pydantic import BaseModel

class User(BaseModel):
   user_id:str
   notes_count:int