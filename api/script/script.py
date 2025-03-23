from pydantic import BaseModel
from typing import List, Optional

class PathNode(BaseModel):
    script: 'Script'
    decision: Optional[str] = None

class Frame(BaseModel):
    narration: str
    description: str

class Script(BaseModel):
    title: str
    frames: List[Frame]
    decisions: List[str]