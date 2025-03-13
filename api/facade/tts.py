from typing import Protocol, Optional, Any

class TTS(Protocol):
    def generate_speech(self, text: str, options: Optional[Any] = None) -> bytes:
        """Generate speech from text."""
        ... 