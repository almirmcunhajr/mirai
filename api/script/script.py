from pydantic import BaseModel
from typing import List

class Frame(BaseModel):
    narration: str
    description: str

class Script(BaseModel):
    title: str
    frames: List[Frame]
    decisions: List[str]