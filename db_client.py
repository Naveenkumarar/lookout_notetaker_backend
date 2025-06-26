from pymongo import MongoClient
from config import config
class DatabaseConnection:
    def __init__(self, ):
        self.mongodb_client = self.startup_db_client()
        self.db = self.mongodb_client[config.DB_NAME]
        self.collection = self.db[config.COLLECTION_NAME]
        self.action_collection=self.db[config.ACTION_COLLECTION_NAME]
        self.user_collection =self.db[config.USER_COLLECTION_NAME]
        self.meeting_collection=self.db[config.MEETING_COLLECTION_NAME]
        self.notification_setting_collection=self.db[config.NOTIFICATION_SETTING]
        self.conversation_collection=self.db[config.CONVERSATION]
        self.meeting_bot=self.db[config.MEETING_BOT]
        self.blocked_users= self.db[config.BLOCKED_USERS]

    def startup_db_client(self):
        mongodb_client = MongoClient(config.MONGO_DB_URL)
        print("MongoDB client started successfully!")
        return mongodb_client