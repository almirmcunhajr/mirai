from enum import Enum
from openai import AsyncOpenAI
from stt.stt import TranscriptionWord

class OpenAIModel(Enum):
    WHISPER_1 = "whisper-1"

class OpenAI:
    def __init__(self, api_key: str, model: OpenAIModel = OpenAIModel.WHISPER_1):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_path: str) -> list[TranscriptionWord]:
        with open(audio_path, "rb") as audio:
            transcript = await self.client.audio.transcriptions.create(
                model=self.model.value,
                file=audio,
                response_format="verbose_json",
                timestamp_granularities=['word']
            )
            return [TranscriptionWord(text=word.word, start=word.start, end=word.end) for word in transcript.words]