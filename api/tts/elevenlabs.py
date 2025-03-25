from tts.tts import SpeechGenerationOptions
from elevenlabs.client import AsyncElevenLabs as ElevenLabsClient
from enum import Enum

class ElevenLabsModel(Enum):
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"

class ElevenLabsVoices(Enum):
    CHARLOTTE = "XB0fDUnXU5powFXDhCwa"

class ElevenLabsOutputFormat(Enum):
    MP3_44100_128 = "mp3_44100_128"

class ElevenLabs:
    def __init__(self, api_key: str, model: ElevenLabsModel = ElevenLabsModel.ELEVEN_MULTILINGUAL_V2):
        self.model = model
        self.client = ElevenLabsClient(api_key=api_key)

    async def to_speech(self, 
        text: str, 
        options: SpeechGenerationOptions = SpeechGenerationOptions(
            voice=ElevenLabsVoices.CHARLOTTE.value, 
            output_format=ElevenLabsOutputFormat.MP3_44100_128.value
        )
    ) -> bytes:
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=options.voice,
            model_id=self.model.value,
            output_format=options.output_format
        )
        
        audio_chunks = []
        async for chunk in audio_generator:
            audio_chunks.append(chunk)
        
        return b''.join(audio_chunks) 