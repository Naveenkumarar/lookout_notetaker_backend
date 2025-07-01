from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings): 

    API_KEY:str = os.getenv("API_KEY")
    AUDIO_FILE_PATH:str = os.getenv("AUDIO_FILE_PATH")
    MONGO_DB_URL:str = os.getenv("MONGO_DB_URL")
    DB_NAME:str = os.getenv("DB_NAME")
    COLLECTION_NAME:str = os.getenv("COLLECTION_NAME")
    ACTION_COLLECTION_NAME:str=os.getenv("ACTION_COLLECTION_NAME")
    NOTE_COLLECTION_NAME:str=os.getenv("NOTE_COLLECTION_NAME")
    ATTENDEE_APP_URL:str = os.getenv("ATTENDEE_APP_URL")
    ATTENDEE_API_KEY:str = os.getenv("ATTENDEE_API_KEY")
    USER_COLLECTION_NAME:str =os.getenv("USER_COLLECTION_NAME")
    MEETING_COLLECTION_NAME:str=os.getenv("MEETING_COLLECTION_NAME")
    NOTIFICATION_SETTING:str=os.getenv("NOTIFICATION_SETTING")
    SHARED_COLLECTION:str=os.getenv("SHARED_COLLECTION")
    CONVERSATION:str=os.getenv("CONVERSATION")
    MEETING_BOT:str=os.getenv("MEETING_BOT")
    EMAIL_USER:str=os.getenv("EMAIL_USER")
    EMAIL_PASS:str=os.getenv("EMAIL_PASS")
    EMAIL_SERVER:str=os.getenv("EMAIL_SERVER")
    EMAIL_PORT:str=os.getenv("EMAIL_PORT")
    EMAIL_FROM:str=os.getenv("EMAIL_FROM")

# get settings 
def get_settings() -> Settings:
    """Get environment specific settings"""
    try:
        settings = Settings()
        print(f"Loaded settings")
        return settings
    except Exception as err:
        print(f"Error loading settings: {str(err)}")
        raise err

# config instance 
config = get_settings() 