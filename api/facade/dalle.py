from openai import AsyncOpenAI
from typing import Optional
from dataclasses import dataclass

@dataclass
class ImageGenerationOptions:
    size: str = "1792x1024"
    quality: str = "standard"
    n: int = 1
    model: str = "dall-e-3"

class DALLE:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_image(self, prompt: str, options: Optional[ImageGenerationOptions] = None) -> str:
        """Generate an image from a text prompt using DALL-E."""
        if options is None:
            options = ImageGenerationOptions()

        response = await self.client.images.generate(
            model=options.model,
            prompt=prompt,
            size=options.size,
            quality=options.quality,
            n=options.n
        )
        return response.data[0].url 