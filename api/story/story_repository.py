from typing import List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient

from database.config import MONGODB_URL, DATABASE_NAME
from story.story import Story

class StoryRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db.stories

    async def create(self, story: Story) -> Story:
        story_dict = story.model_dump()
        story_dict["id"] = str(story_dict["id"])
        story_dict["root_node_id"] = str(story_dict["root_node_id"])
        
        for node in story_dict["nodes"]:
            node["id"] = str(node["id"])
            if node["parent_id"]:
                node["parent_id"] = str(node["parent_id"])
            node["children"] = [str(child_id) for child_id in node["children"]]
        
        result = await self.collection.insert_one(story_dict)
        
        return await self.get_by_id(story.id)

    async def get_by_id(self, story_id: UUID) -> Optional[Story]:
        story_dict = await self.collection.find_one({"id": str(story_id)})
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

    async def update(self, story: Story) -> Optional[Story]:
        story_dict = story.model_dump()
        story_dict["id"] = str(story_dict["id"])
        story_dict["root_node_id"] = str(story_dict["root_node_id"])
        
        for node in story_dict["nodes"]:
            node["id"] = str(node["id"])
            if node["parent_id"]:
                node["parent_id"] = str(node["parent_id"])
            node["children"] = [str(child_id) for child_id in node["children"]]
        
        result = await self.collection.update_one(
            {"id": str(story.id)},
            {"$set": story_dict}
        )
        
        if result.modified_count == 0:
            return None
            
        return await self.get_by_id(story.id)

    async def delete(self, story_id: UUID) -> bool:
        result = await self.collection.delete_one({"id": str(story_id)})
        return result.deleted_count > 0

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