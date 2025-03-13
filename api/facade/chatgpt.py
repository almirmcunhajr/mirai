from openai import OpenAI
from typing import Optional

from .chatbot import Chatbot, ImageGenerationOptions, TextGenerationOptions

class ChatGPT(Chatbot):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_response(self, text: str, options: Optional[TextGenerationOptions] = None) -> str:
        """General purpose text completion method."""
        if options is None:
            options = TextGenerationOptions()

        completion = self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": "user", "content": text}]
        )
        return completion.choices[0].message.content

    def generate_image(self, prompt: str, options: Optional[ImageGenerationOptions] = None) -> str:
        """Generate an image from a text prompt using DALL-E."""
        if options is None:
            options = ImageGenerationOptions()

        response = self.client.images.generate(
            model=options.model,
            prompt=prompt,
            size=options.size,
            quality=options.quality,
            n=options.n
        )
        return response.data[0].url