from pydantic import (BaseModel)
from datetime import datetime

class Meeting(BaseModel):
   user_id:str
   link:str
   title:str
   start_time:datetime = None
   end_time:datetime = None
