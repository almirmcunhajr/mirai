from openai import OpenAI
from typing import Optional
from dataclasses import dataclass

from .chatbot import Chatbot

@dataclass
class TextGenerationOptions:
    model: str = "gpt-4o-mini"

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