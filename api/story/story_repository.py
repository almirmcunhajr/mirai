from typing import List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient

from database.config import MONGODB_URL, DATABASE_NAME
from story.story import Story

class StoryRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL, uuidRepresentation="standard")
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db.stories

    async def find_by_id(self, story_id: UUID, user_id: str) -> Optional[Story]:
        story = await self.collection.find_one({"id": story_id, "user_id": user_id})
        return Story(**story) if story else None

    async def find_all_by_user(self, user_id: str) -> List[Story]:
        cursor = self.collection.find({"user_id": user_id})
        stories = await cursor.to_list(length=None)
        return [Story(**story) for story in stories]

    async def create(self, story: Story) -> Story:
        result = await self.collection.insert_one(story.model_dump())
        return story

    async def update(self, story: Story) -> Story:
        await self.collection.update_one(
            {"id": story.id, "user_id": story.user_id},
            {"$set": story.model_dump()}
        )
        return story

    async def delete(self, story_id: UUID, user_id: str) -> bool:
        result = await self.collection.delete_one({"id": story_id, "user_id": user_id})
        return result.deleted_count > 0

    async def get_by_id(self, story_id: UUID) -> Optional[Story]:
        story_dict = await self.collection.find_one({"id": story_id})
        if not story_dict:
            return None
            
        story_dict["id"] = UUID(story_dict["id"])
        story_dict["root_node_id"] = UUID(story_dict["root_node_id"])
        
        for node in story_dict["nodes"]:
            node["id"] = UUID(node["id"])
            if node["parent_id"]:
                node["parent_id"] = UUID(node["parent_id"])
            node["children"] = [UUID(child_id) for child_id in node["children"]]
        
        return Story(**story_dict)

    async def list_stories(self) -> List[Story]:
        stories = []
        cursor = self.collection.find()
        
        async for story_dict in cursor:
            story_dict["id"] = UUID(story_dict["id"])
            story_dict["root_node_id"] = UUID(story_dict["root_node_id"])
            
            for node in story_dict["nodes"]:
                node["id"] = UUID(node["id"])
                if node["parent_id"]:
                    node["parent_id"] = UUID(node["parent_id"])
                node["children"] = [UUID(child_id) for child_id in node["children"]]
            
            stories.append(Story(**story_dict))
            
        return stories 