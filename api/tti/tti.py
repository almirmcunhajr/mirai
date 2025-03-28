from typing import Protocol
from pydantic import BaseModel
from enum import Enum

class ImageGenerationOptions(BaseModel):
    width: int = 1792
    height: int = 1024

class TTI(Protocol):
    async def to_image(self, prompt: str, options: ImageGenerationOptions) -> bytes:
        ... 