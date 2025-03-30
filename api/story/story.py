from pydantic import Field, BaseModel
from typing import Optional, Literal
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import StrEnum

from script.script import Script
from common.genre import Genre
from ttt.ttt import Chat

class Style(StrEnum):
    CARTOON = "cartoon"
    REALISTIC = "realistic"
    ANIME = "anime"

class Character(BaseModel):
    name: str
    age: int
    gender: Literal["male", "female"]
    voice_id: str = None

class StoryNode(BaseModel):
    """Represents a node in the story tree."""
    id: UUID = Field(default_factory=uuid4)
    characters: list[Character]
    script: Script
    decision: Optional[str] = None
    parent_id: Optional[UUID] = None
    children: list[UUID] = []
    video_url: Optional[str] = None
    chat: Chat
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Story(BaseModel):
    """Represents a complete story tree."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    genre: Genre
    style: Style
    language: str
    root_node_id: UUID
    nodes: list[StoryNode] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))