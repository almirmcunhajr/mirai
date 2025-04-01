from together import Together as TogetherClient
from enum import Enum

from tti.tti import ImageGenerationOptions

class TogetherModel(Enum):
    FLUX_1_SCHNELL_FREE = "black-forest-labs/FLUX.1-schnell-Free"
    FLUX_1_DEV = "black-forest-labs/FLUX.1-dev"

class Together:
    def __init__(self, api_key: str = None, model: TogetherModel = TogetherModel.FLUX_1_DEV, base_url: str = None):
        self.model = model
        self.client = TogetherClient(api_key=api_key, base_url=base_url)
    
    async def to_image(self, prompt: str, options: ImageGenerationOptions = ImageGenerationOptions()) -> bytes:
        response = self.client.images.generate(
            model=self.model.value,
            prompt=prompt,
            width=options.width,
            height=options.height,
            n=1,
            steps=28,
            stop=[],
            response_format='b64_json',
        )
        return response.data[0].b64_json