from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from script.script import Script
from common.genre import Genre

class StoryNode(BaseModel):
    """Represents a node in the story tree."""
    id: UUID = uuid4()
    script: Script
    decision: Optional[str] = None  # The decision that led to this node
    parent_id: Optional[UUID] = None  # Reference to parent node
    children: List[UUID] = []  # List of child node IDs
    video_url: Optional[str] = None  # URL to the generated video for this branch
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class Story(BaseModel):
    """Represents a complete story tree."""
    id: UUID = uuid4()
    title: str
    genre: Genre
    root_node_id: UUID  # Reference to the root node
    nodes: List[StoryNode] = []  # All nodes in the tree
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow() 