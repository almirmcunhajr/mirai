from typing import Protocol
from story.story import Character
from pydantic import BaseModel

class SpeechGenerationOptions(BaseModel):
    voice: str = None

class SoundEffectGenerationOptions(BaseModel):
    duration: float = None

class TTS(Protocol):
    async def to_speech(self, text: str, options: SpeechGenerationOptions) -> bytes:
        ... 
    
    async def get_voice(self, language: str, used_voices: list[str] = [],character: Character = None) -> str:
        ...

    async def to_sound_effect(self, text: str, options: SoundEffectGenerationOptions) -> bytes:
        ...