from pydantic import Field, BaseModel
from typing import Optional, Union, Annotated, Literal
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

class SubjectType(StrEnum):
    ENVIRONMENT = "environment"
    CHARACTER = "character"

class CharacterGender(StrEnum):
    MALE = "male"
    FEMALE = "female"

class Subject(BaseModel):
    type: SubjectType
    name: str
    description: str

class Environment(Subject):
    type: Literal[SubjectType.ENVIRONMENT] = SubjectType.ENVIRONMENT
      
class Character(Subject):
    type: Literal[SubjectType.CHARACTER] = SubjectType.CHARACTER
    age: int
    gender: CharacterGender
    voice_id: Optional[str] = None

class PathNode(BaseModel):
    script: Script
    decision: Optional[str] = None

class StoryNode(BaseModel):
    """Represents a node in the story tree."""
    id: UUID = Field(default_factory=uuid4)
    subjects: dict[str, Annotated[Union[Character, Environment], Field(discriminator='type')]] = {}
    script: Script
    decision: Optional[str] = None
    parent_id: Optional[UUID] = None
    children: list[UUID] = []
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    chat: Chat
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Story(BaseModel):
    """Represents a complete story tree."""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    title: str
    genre: Genre
    style: Style
    language: str
    root_node_id: UUID
    nodes: list[StoryNode] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))