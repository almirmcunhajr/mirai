from common.base_model_no_extra import BaseModelNoExtra 

class TranscriptionWord(BaseModelNoExtra):
    text: str
    start: float
    end: float

class STT:
    async def transcribe(self, audio_path: str) -> list[TranscriptionWord]:
        pass
