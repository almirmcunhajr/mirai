from typing import Protocol, Optional
from dataclasses import dataclass

@dataclass
class ImageGenerationOptions:
    size: str = "1792x1024"
    quality: str = "standard"
    n: int = 1
    model: str = "dall-e-3"

@dataclass
class TextGenerationOptions:
    model: str = "gpt-4"

class Chatbot(Protocol):
    def get_response(self, text: str, options: Optional[TextGenerationOptions] = None) -> str:
        """General purpose text completion method."""
        ...

    def generate_image(self, prompt: str, options: Optional[ImageGenerationOptions] = None) -> str:
        """Generate an image from a text prompt."""
        ...