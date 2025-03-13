from openai import OpenAI
from typing import Optional
from dataclasses import dataclass

from .tts import TTS

@dataclass
class OpenAITTSOptions:
    model: str = "tts-1"
    voice: str = "fable"

class OpenAITTS(TTS):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_speech(self, text: str, options: Optional[OpenAITTSOptions] = None) -> bytes:
        """Generate speech from text using OpenAI's text-to-speech API."""
        if options is None:
            options = OpenAITTSOptions()

        response = self.client.audio.speech.create(
            model=options.model,
            voice=options.voice,
            input=text
        )
        return response.content 