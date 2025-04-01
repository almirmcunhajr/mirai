from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from database.config import MONGODB_URL, DATABASE_NAME
from user.user import User

class UserRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db.users

    async def find_by_email(self, email: str) -> Optional[User]:
        user = await self.collection.find_one({"email": email})
        return User(**user) if user else None

    async def find_by_id(self, user_id: str) -> Optional[User]:
        user = await self.collection.find_one({"id": user_id})
        return User(**user) if user else None

    async def create(self, user_data: Dict[str, Any]) -> User:
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data.get("name", "")
        )
        result = await self.collection.insert_one(user.model_dump())
        return user

    async def update_last_login(self, email: str) -> User:
        user = await self.collection.find_one_and_update(
            {"email": email},
            {"$set": {"last_login": datetime.now()}},
            return_document=True
        )
        return User(**user) 