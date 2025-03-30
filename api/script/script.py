from typing import Optional, Literal
from common.genre import Genre
from common.base_model_no_extra import BaseModelNoExtra

class PathNode(BaseModelNoExtra):
    script: 'Script'
    decision: Optional[str] = None

class Line(BaseModelNoExtra):
    type: Literal["dialogue", "narration"]
    character: str
    line: str

class Scene(BaseModelNoExtra):
    id: int
    visual_description: str
    lines: list[Line]

class Script(BaseModelNoExtra):
    title: str
    genre: Genre
    language: str
    scenes: list[Scene]
    end: bool
