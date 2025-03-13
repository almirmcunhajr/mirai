from typing import List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

from database.config import MONGODB_URL, DATABASE_NAME
from story.story import Story, StoryNode

class StoryRepository:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db.stories

    async def create(self, story: Story) -> Story:
        """
        Creates a new story in the database.
        
        Args:
            story (Story): The story to create
            
        Returns:
            Story: The created story
        """
        # Convert UUIDs to strings for MongoDB
        story_dict = story.model_dump()
        story_dict["id"] = str(story_dict["id"])
        story_dict["root_node_id"] = str(story_dict["root_node_id"])
        
        # Convert node UUIDs to strings
        for node in story_dict["nodes"]:
            node["id"] = str(node["id"])
            if node["parent_id"]:
                node["parent_id"] = str(node["parent_id"])
            node["children"] = [str(child_id) for child_id in node["children"]]
        
        # Insert into database
        result = await self.collection.insert_one(story_dict)
        
        # Convert back to Story object
        return await self.get_by_id(story.id)

    async def get_by_id(self, story_id: UUID) -> Optional[Story]:
        """
        Gets a story by its ID.
        
        Args:
            story_id (UUID): The story ID
            
        Returns:
            Optional[Story]: The story if found, None otherwise
        """
        story_dict = await self.collection.find_one({"id": str(story_id)})
        if not story_dict:
            return None
            
        # Convert string IDs back to UUIDs
        story_dict["id"] = UUID(story_dict["id"])
        story_dict["root_node_id"] = UUID(story_dict["root_node_id"])
        
        # Convert node string IDs back to UUIDs
        for node in story_dict["nodes"]:
            node["id"] = UUID(node["id"])
            if node["parent_id"]:
                node["parent_id"] = UUID(node["parent_id"])
            node["children"] = [UUID(child_id) for child_id in node["children"]]
        
        return Story(**story_dict)

    async def update(self, story: Story) -> Optional[Story]:
        """
        Updates a story in the database.
        
        Args:
            story (Story): The story to update
            
        Returns:
            Optional[Story]: The updated story if found, None otherwise
        """
        # Convert UUIDs to strings for MongoDB
        story_dict = story.model_dump()
        story_dict["id"] = str(story_dict["id"])
        story_dict["root_node_id"] = str(story_dict["root_node_id"])
        
        # Convert node UUIDs to strings
        for node in story_dict["nodes"]:
            node["id"] = str(node["id"])
            if node["parent_id"]:
                node["parent_id"] = str(node["parent_id"])
            node["children"] = [str(child_id) for child_id in node["children"]]
        
        # Update in database
        result = await self.collection.update_one(
            {"id": str(story.id)},
            {"$set": story_dict}
        )
        
        if result.modified_count == 0:
            return None
            
        return await self.get_by_id(story.id)

    async def delete(self, story_id: UUID) -> bool:
        """
        Deletes a story from the database.
        
        Args:
            story_id (UUID): The story ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"id": str(story_id)})
        return result.deleted_count > 0

    async def list_stories(self) -> List[Story]:
        """
        Lists all stories in the database.
        
        Returns:
            List[Story]: List of stories
        """
        stories = []
        cursor = self.collection.find()
        
        async for story_dict in cursor:
            # Convert string IDs back to UUIDs
            story_dict["id"] = UUID(story_dict["id"])
            story_dict["root_node_id"] = UUID(story_dict["root_node_id"])
            
            # Convert node string IDs back to UUIDs
            for node in story_dict["nodes"]:
                node["id"] = UUID(node["id"])
                if node["parent_id"]:
                    node["parent_id"] = UUID(node["parent_id"])
                node["children"] = [UUID(child_id) for child_id in node["children"]]
            
            stories.append(Story(**story_dict))
            
        return stories 