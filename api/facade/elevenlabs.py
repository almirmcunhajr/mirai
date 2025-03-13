from typing import Optional
from elevenlabs import Client

from .tts import TTSOptions

class ElevenLabs:
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)

    def generate_speech(self, text: str, options: Optional[TTSOptions] = None) -> bytes:
        """Generate speech from text using ElevenLabs."""
        if options is None:
            options = TTSOptions()

        return self.client.generate(
            text=text,
            voice_id=options.voice_id,
            model=options.model,
            voice_settings=options.voice_settings,
            output_format=options.output_format
        ) 