from pydantic import BaseModel

class TranscriptionWord(BaseModel):
    text: str
    start: float
    end: float

class STT:
    async def transcribe(self, audio_path: str) -> list[TranscriptionWord]:
        pass
