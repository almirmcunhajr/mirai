from pydantic import BaseModel
from typing import List, Optional

class PathNode(BaseModel):
    """Represents a node in the story path."""
    script: 'Script'
    decision: str

class Frame(BaseModel):
    """Represents a single frame in the script."""
    narration: str
    description: str

class Script(BaseModel):
    """Represents a script with frames and possible decisions."""
    title: str
    frames: List[Frame]
    decisions: List[str]