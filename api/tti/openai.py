from openai import AsyncOpenAI
from enum import Enum

from tti.tti import ImageGenerationOptions

class OpenAIModel(Enum):
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"

class OpenAI:
    def __init__(self, api_key: str = None, model: OpenAIModel = OpenAIModel.DALL_E_3, base_url: str = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def to_image(self, prompt: str, options: ImageGenerationOptions = ImageGenerationOptions()) -> bytes:
        response = await self.client.images.generate(
            model=self.model.value,
            prompt=prompt,
            size=f'{options.width}x{options.height}',
            n=1,
            response_format='b64_json',
        )
        return response.data[0].b64_json.encode('ascii')
