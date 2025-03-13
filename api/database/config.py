import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mirai") 