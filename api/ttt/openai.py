from openai import AsyncOpenAI
from typing import Optional
from dataclasses import dataclass

from .ttt import TTT

@dataclass
class TextGenerationOptions:
    model: str = "gpt-4o-mini"

class OpenAI(TTT):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_text(self, text: str, options: Optional[TextGenerationOptions] = None) -> str:
        """General purpose text completion method."""
        if options is None:
            options = TextGenerationOptions()

        completion = await self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": "user", "content": text}]
        )
        return completion.choices[0].message.content