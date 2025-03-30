from typing import Optional, Literal
from common.genre import Genre
from pydantic import BaseModel

class Line(BaseModel):
    type: Literal["dialogue", "narration"]
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
