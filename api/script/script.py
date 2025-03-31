from typing import Optional
from enum import StrEnum

from pydantic import BaseModel

from common.genre import Genre

class LineType(StrEnum):
    DIALOGUE = "dialogue"
    NARRATION = "narration"

class Line(BaseModel):
    type: LineType
    character_id: Optional[int]
    line: str

class Scene(BaseModel):
    id: int
    visual_description: str
    lines: list[Line]

class Script(BaseModel):
    title: str
    genre: Genre
    language: str
    scenes: list[Scene]
    end: bool
