from typing import Protocol, Optional
from dataclasses import dataclass
from elevenlabs.api import Voice, VoiceSettings

@dataclass
class TTSOptions:
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice: Rachel
    model: str = "eleven_multilingual_v2"
    voice_settings: Optional[VoiceSettings] = VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True
    )
    output_format: str = "mp3"

class TTS(Protocol):
    def generate_speech(self, text: str, options: Optional[TTSOptions] = None) -> bytes:
        """Generate speech from text."""
        ... 