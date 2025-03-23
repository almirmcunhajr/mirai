from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from script.script import Script
from common.genre import Genre
from ttt.ttt import Chat

class StoryNode(BaseModel):
    """Represents a node in the story tree."""
    id: UUID = uuid4()
    script: Script
    decision: Optional[str] = None
    parent_id: Optional[UUID] = None
    children: List[UUID] = []
    video_url: Optional[str] = None
    chat: Chat
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

class Story(BaseModel):
    """Represents a complete story tree."""
    id: UUID = uuid4()
    title: str
    genre: Genre
    root_node_id: UUID
    nodes: List[StoryNode] = []
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)