from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
AUDIO_FILE_PATH = os.getenv("AUDIO_FILE_PATH")
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ACTION_COLLECTION_NAME=os.getenv("ACTION_COLLECTION_NAME")
NOTE_COLLECTION_NAME=os.getenv("NOTE_COLLECTION_NAME")
ATTENDEE_APP_URL = os.getenv("ATTENDEE_APP_URL")
ATTENDEE_API_KEY = os.getenv("ATTENDEE_API_KEY")
