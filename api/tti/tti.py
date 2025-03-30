from typing import Protocol
from common.base_model_no_extra import BaseModelNoExtra

class ImageGenerationOptions(BaseModelNoExtra):
    width: int = 1280
    height: int = 720

class TTI(Protocol):
    async def to_image(self, prompt: str, options: ImageGenerationOptions) -> bytes:
        ... 