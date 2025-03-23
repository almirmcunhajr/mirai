from typing import Protocol
from pydantic import BaseModel

class ImageGenerationOptions(BaseModel):
    size: str = None
    quality: str = None
    n: int = None

class TTI(Protocol):
    async def to_image(self, prompt: str, options: ImageGenerationOptions) -> bytes:
        """Generate an image from a text prompt."""
        ... 