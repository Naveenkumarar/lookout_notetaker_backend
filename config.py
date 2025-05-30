from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
AUDIO_FILE_PATH = os.getenv("AUDIO_FILE_PATH")
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")