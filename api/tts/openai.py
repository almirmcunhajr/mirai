from enum import Enum

from openai import AsyncOpenAI

from tts.tts import TTS, SpeechGenerationOptions
from story.story import Character

class OpenAIModel(Enum):
    TTS_1 = "tts-1"
    
class OpenAI(TTS):
    def __init__(self, api_key: str = None, model: OpenAIModel = OpenAIModel.TTS_1, base_url: str = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def to_speech(self, 
        text: str, 
        options: SpeechGenerationOptions
    ) -> bytes:
        response = await self.client.audio.speech.create(
            model=self.model.value,
            voice=options.voice,
            input=text
        )
        return response.content 
    
    def get_voice(self, language: str, used_voices: list[str] = [],character: Character = None) -> str:
        return 'fable'