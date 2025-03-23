from typing import Protocol, Optional, Any

class TTS(Protocol):
    async def generate_speech(self, text: str, options: Optional[Any] = None) -> bytes:
        """Generate speech from text."""
        ... 