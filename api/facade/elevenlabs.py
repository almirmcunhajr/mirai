from typing import Optional
from elevenlabs.client import ElevenLabs as ElevenLabsClient

from .tts import TTSOptions

class ElevenLabs:
    def __init__(self, api_key: str):
        self.client = ElevenLabsClient(api_key=api_key)

    def generate_speech(self, text: str, options: Optional[TTSOptions] = None) -> bytes:
        """Generate speech from text using ElevenLabs."""
        if options is None:
            options = TTSOptions()

        # Convert the generator to bytes
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=options.voice_id,
            model_id=options.model,
            output_format=options.output_format
        )
        return b''.join(audio_generator) 