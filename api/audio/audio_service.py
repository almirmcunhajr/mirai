import logging
import asyncio
import os
from typing import Literal

from tts.tts import TTS, SpeechGenerationOptions, SoundEffectGenerationOptions
from stt.stt import STT
from ttt.ttt import TTT, Chat, ChatOptions
from script.script import Line, LineType
from story.story import Subject, Character
from audio.exceptions import AudioGenerationError
from audio.audio import LineAudio, SoundEffectAudio, SoundEffectType
from common.base_model_no_extra import BaseModelNoExtra
from utils.utils import generate_random_string, exponential_backoff_call

from moviepy.audio.io.AudioFileClip import AudioFileClip

class SoundDescriptionRespone(BaseModelNoExtra):
    description: str
    start_time: float
    end_time: float
    type: Literal[SoundEffectType.SOUND_EFFECT, SoundEffectType.AMBIENT]

class SoundEffectsDescriptionsResponse(BaseModelNoExtra):
    sound_effects_descriptions: list[SoundDescriptionRespone]

class AudioService:
    def __init__(self, tts: TTS, stt: STT, ttt: TTT, max_concurrent_requests: int = 2):
        self.tts = tts
        self.stt = stt
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def _format_line_audio_for_sound_effects_desctiption_prompt(self, line_audio: LineAudio) -> str:
        line_start = line_audio.clip.start
        return ", ".join([f'({word.text}, {word.start+line_start}, {word.end+line_start})' for word in line_audio.transcription])

    def _get_sound_effects_description_prompt(self, lines_audios: list[LineAudio]) -> str:
        transcription = '\n'.join([f'{line_audio.type}: {self._format_line_audio_for_sound_effects_desctiption_prompt(line_audio)}' for line_audio in lines_audios])
        return f'''You are a sound design assistant. Your job is to analyze a scene and return a list of **event-based sound effects** and **continuous ambient background sounds** that match both the transcription and the visual context.

You will be provided with:

1. A transcription, segmented by word in the format: `(word, start_time, end_time)`.  
2. An image that visually describes the scene.

Your task is to output a JSON. Each element must include:

- **"description"**: a realistic and detailed description of the sound, suitable for a text-to-sound model. Sounds must not include human voices, names, pronouns, or music.  
- **"start_time"**: the precise float (in seconds) when the sound begins.  
- **"end_time"**: the precise float (in seconds) when the sound ends. The duration must be at least **5.0 second** and at most **22.0 seconds**.
- **"type"**: the type of sound, either "sound_effect" or "ambient".

---

### Rules

- Use the transcription to identify **transient physical actions or events** that require momentary sound effects (e.g., a door slamming, a car passing, a glass breaking).
  - Sound effects must be **short and action-specific**, representing quick, isolated moments.
  - Only include sound effects if they are clearly motivated by the transcription.
- Use the image to identify **continuous ambient sounds** that represent the **environmental background** of the scene (e.g., rain falling, wind through trees, ocean waves, city traffic).
  - These ambient sounds must reflect **persistent elements** in the scene.
  - For example, if trees are visible, the rustling of leaves in the wind should be audible throughout the entire scene — not briefly.
  - Each background sound must **last the full duration of the scene**, up to a maximum of **22.0 seconds**.
- Ambient sounds and sound effects may overlap when appropriate, as long as they do not conflict.
- Spoken language (dialogue or narration) is strictly prohibited.
  - However, **non-verbal human sounds** (e.g., gasps, coughs, footsteps, distant murmur) are allowed when clearly relevant.
- **Do not include music in any sound.**
- Do not include names or pronouns in any description.
- You may generate up to **2 background sounds** and up to **4 sound effects**, but only when justified by the scene.

---

### Transcription  
{transcription}

'''

    async def _generate_sound_effect_audio(self, description_response: SoundDescriptionRespone, audio_file_path: str) -> SoundEffectAudio:
        try:
            async with self.semaphore:
                duration = min(max(description_response.end_time-description_response.start_time, 0.5), 22)
                options = SoundEffectGenerationOptions(duration=duration)
                self.logger.info(f"Generating sound effect")
                audio_data = await exponential_backoff_call(self.tts.to_sound_effect, description_response.description, options)

                with open(audio_file_path, "wb") as f:
                    f.write(audio_data)

                self.logger.info(f"Saved sound effect audio file to")

                clip = AudioFileClip(audio_file_path).with_start(description_response.start_time)

                self.logger.info(f'Generated sound effect for:\nDescription: {description_response.description}\nStart time: {description_response.start_time}\nEnd time: {description_response.end_time}\nType: {description_response.type}\n With duration {clip.duration}')

                return SoundEffectAudio(
                    clip=clip,
                    type=description_response.type
                )
        except Exception as e:
            raise AudioGenerationError(f"Failed to generate sound effect audio: {str(e)}")

    async def generate_sound_effects_audios(self, lines_audios: list[LineAudio], scene_base64_image: str, dir_path: str) -> list[SoundEffectAudio]:
        chat = Chat()
        prompt = self._get_sound_effects_description_prompt(lines_audios)
        chat.add_user_message([
            {
                "type": "input_text",
                "text": prompt
            },
            {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{scene_base64_image}",
                "detail": "low"
            }
        ])
        chat_options = ChatOptions(response_format=SoundEffectsDescriptionsResponse)
        sound_effects_desctiptions_response: SoundEffectsDescriptionsResponse = await self.ttt.chat(chat, chat_options)

        tasks = [
            self._generate_sound_effect_audio(
                sound_effect_description,
                os.path.join(dir_path, f"{generate_random_string()}.mp3")
            )
            for i, sound_effect_description in enumerate(sound_effects_desctiptions_response.sound_effects_descriptions)
        ]
        sound_effects_audios = await asyncio.gather(*tasks)
        self.logger.info(f"Generated {len(sound_effects_audios)} sound effects audios")

        return sound_effects_audios

    async def generate_line_audio(self, line: Line, language: str, subjects: dict[str, Subject], audio_file_path: str) -> LineAudio:
        characters = [subject for subject in subjects.values() if isinstance(subject, Character)]
        try:
            async with self.semaphore:
                options = SpeechGenerationOptions()
                if line.type == LineType.DIALOGUE:
                    character: Character = subjects[str(line.character_id)]
                    if not character.voice_id:
                        self.logger.info(f"Getting voice for character {character.name}")
                        used_voices = set([c.voice_id for c in characters if c.voice_id is not None])
                        character.voice_id = await self.tts.get_voice(language, used_voices, character)
                    options.voice = character.voice_id
                else:
                    options.voice = await exponential_backoff_call(self.tts.get_voice, language, [], None)
                self.logger.info(f"Generating {line.type} audio with voice {options.voice}")
                audio_data = await exponential_backoff_call(self.tts.to_speech, line.line, options)
                
                with open(audio_file_path, "wb") as f:
                    f.write(audio_data)
                
                self.logger.info(f"Saved {line.type} audio file to {audio_file_path}")

                self.logger.info(f'Generating line transcription')
                transctiption = await self.stt.transcribe(audio_file_path)

                return LineAudio(
                    clip=AudioFileClip(audio_file_path),
                    transcription=transctiption,
                    type=line.type
                )
                    
        except Exception as e:
            raise AudioGenerationError(f"Failed to generate line audio: {str(e)}")
