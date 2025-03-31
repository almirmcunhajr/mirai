from enum import Enum
import random

from tts.tts import SpeechGenerationOptions, SoundEffectGenerationOptions
from elevenlabs.client import AsyncElevenLabs as ElevenLabsClient
from elevenlabs.types import Voice
from story.story import Character, CharacterGender

class ElevenLabsModel(Enum):
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"

class ElevenLabsOutputFormat(Enum):
    MP3_44100_128 = "mp3_44100_128"

class ElevenLabs:
    def __init__(self, api_key: str, model: ElevenLabsModel = ElevenLabsModel.ELEVEN_MULTILINGUAL_V2):
        self.model = model
        self.client = ElevenLabsClient(api_key=api_key)

    async def to_sound_effect(self, 
        text: str,
        options: SoundEffectGenerationOptions = SoundEffectGenerationOptions()
    ) -> bytes:
        audio_generator = self.client.text_to_sound_effects.convert(
            text=text,
            duration_seconds=options.duration,
        )

        audio_chunks = []
        async for chunk in audio_generator:
            audio_chunks.append(chunk)
        
        return b''.join(audio_chunks) 

    async def to_speech(self, 
        text: str, 
        options: SpeechGenerationOptions = SpeechGenerationOptions()
    ) -> bytes:
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=options.voice,
            model_id=self.model.value,
        )
        
        audio_chunks = []
        async for chunk in audio_generator:
            audio_chunks.append(chunk)
        
        return b''.join(audio_chunks) 
    
    def _get_voice_age(self, character: Character) -> str:
        if character.age <= 29:
            return "young"
        if character.age >= 30 and character.age <= 59:
            return "middle-aged"
        if character.age >= 60:
            return "old"
    
    def _get_voice_gender(self, character: Character) -> str:
        if character.gender == CharacterGender.MALE:
            return "male"
        if character.gender == CharacterGender.FEMALE:
            return "female"
        return "neutral"
    
    async def get_voice(self, language: str, used_voices: list[str] = [], character: Character = None) -> str:
        if not character:
            return "pFZP5JQG7iQjIQuC4Bku" # Lily

        response = await self.client.voices.search(page_size=100)
        voice_id = None
        while True:
            random.shuffle(response.voices)
            for voice in response.voices:
                if voice.voice_id in used_voices:
                    continue
                if voice.labels['gender'] != self._get_voice_gender(character):
                    continue
                if voice.labels['use_case'] == 'asmr':
                    continue
                if not voice_id:
                    voice_id = voice.voice_id
                if 'language' not in voice.labels or voice.labels['language'] == language.split('-')[0]:
                    voice_id = voice.voice_id
                if voice.labels['age'] == self._get_voice_age(character):
                    voice_id = voice.voice_id
                if voice.labels['use_case'] == 'character':
                    return voice.voice_id
            if not response.has_more:
                break
            response = await self.client.voices.search(page_size=100, next_page_token=response.next_page_token)

        if not voice_id:
            raise Exception("No voice found")
        return voice_id