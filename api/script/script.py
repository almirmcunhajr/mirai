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

class Ending(BaseModelNoExtra):
    type: Literal["decision", "end"]
    description: str

class Character(BaseModelNoExtra):
    name: str
    age: int
    gender: Literal["male", "female"]
    voice_id: str = None

class Script(BaseModelNoExtra):
    title: str
    genre: Genre
    language: str
    scenes: list[Scene]
    characters: list[Character]
    ending: Ending
