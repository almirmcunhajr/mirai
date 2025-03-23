from enum import Enum

from openai import AsyncOpenAI

from tts.tts import TTS, SpeechGenerationOptions

class OpenAIModel(Enum):
    TTS_1 = "tts-1"

class OpenAIVoices(Enum):
    FABLE = "fable"
    
class OpenAI(TTS):
    def __init__(self, api_key: str = None, model: OpenAIModel = OpenAIModel.TTS_1, base_url: str = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def to_speech(self, 
        text: str, 
        options: SpeechGenerationOptions = SpeechGenerationOptions(
            voice=OpenAIVoices.FABLE.value
        )
    ) -> bytes:
        """Generate speech from text using OpenAI's text-to-speech API."""

        response = await self.client.audio.speech.create(
            model=self.model.value,
            voice=options.voice,
            input=text
        )
        return response.content 