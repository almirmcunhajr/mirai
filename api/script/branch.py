from pydantic import BaseModel

from script.script import Script

class Branch(BaseModel):
    script: Script
    decision: str