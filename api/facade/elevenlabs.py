from typing import Optional
from dataclasses import dataclass
from elevenlabs.client import ElevenLabs as ElevenLabsClient

@dataclass
class TTSOptions:
    voice_id: str = "XB0fDUnXU5powFXDhCwa"  # Charlotte
    model: str = "eleven_multilingual_v2"
    output_format: str = "mp3_44100_128"

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