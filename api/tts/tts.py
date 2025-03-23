from typing import Protocol
from pydantic import BaseModel

class SpeechGenerationOptions(BaseModel):
    voice: str = None
    output_format: str = None

class TTS(Protocol):
    async def to_speech(self, text: str, options: SpeechGenerationOptions) -> bytes:
        """Generate speech from text."""
        ... 