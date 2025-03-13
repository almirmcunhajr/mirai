from typing import Protocol, Optional
from dataclasses import dataclass

@dataclass
class TTSOptions:
    voice_id: str = "XB0fDUnXU5powFXDhCwa"  # Default voice: Rachel
    model: str = "eleven_multilingual_v2"
    output_format: str = "mp3_44100_128"  # High-quality MP3 format

class TTS(Protocol):
    def generate_speech(self, text: str, options: Optional[TTSOptions] = None) -> bytes:
        """Generate speech from text."""
        ... 