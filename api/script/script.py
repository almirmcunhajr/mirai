from pydantic import BaseModel
from typing import List, Optional

class PathNode(BaseModel):
    script: 'Script'
    decision: Optional[str] = None

class Scene(BaseModel):
    narration: str
    description: str

class Script(BaseModel):
    title: str
    scenes: List[Scene]
    decisions: List[str]