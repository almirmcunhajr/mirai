from typing import Protocol
from story.story import Character
from common.base_model_no_extra import BaseModelNoExtra

class SpeechGenerationOptions(BaseModelNoExtra):
    voice: str = None
    output_format: str = None

class TTS(Protocol):
    async def to_speech(self, text: str, options: SpeechGenerationOptions) -> bytes:
        ... 
    
    async def get_voice(self, language: str, used_voices: list[str] = [],character: Character = None) -> str:
        ...