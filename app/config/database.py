import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            try:
                cls.client = MongoClient(os.getenv("MONGODB_URI"))
                cls.db = cls.client[os.getenv("DATABASE_NAME")]
                print("Connected to MongoDB successfully!")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                raise e

    @classmethod
    def get_database(cls):
        if cls.db is None:
            cls.connect()
        return cls.db

    @classmethod
    def close_connection(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("MongoDB connection closed.")