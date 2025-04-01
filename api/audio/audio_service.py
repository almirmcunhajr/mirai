import logging
import asyncio
import os

from tts.tts import TTS, SpeechGenerationOptions, SoundEffectGenerationOptions
from stt.stt import STT
from ttt.ttt import TTT, Chat, ChatOptions
from script.script import Line, LineType
from story.story import Subject, Character
from audio.exceptions import AudioGenerationError
from audio.audio import LineAudio, SoundEffectAudio
from common.base_model_no_extra import BaseModelNoExtra
from utils.utils import generate_random_string, exponential_backoff_call

from moviepy.audio.io.AudioFileClip import AudioFileClip

class SoundDescriptionRespone(BaseModelNoExtra):
    description: str
    start_time: float
    end_time: float

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
        return f'''You are a sound design assistant. Your job is to analyze a scene and return a list of **sound effects** and **ambient background sounds** that match both the transcription and the visual.

You will be provided with:

1. A transcription, segmented by word in the format: `(word, start_time, end_time)`  
2. An image that visually describes the scene.

Your task is to output a JSON. Each element must include:

- **"description"**: a realistic and detailed description of the sound, suitable for a text-to-sound model. The sound must not include any human voice, names, pronouns, or music.  
- **"start_time"**: the precise float (in seconds) when the sound begins.  
- **"end_time"**: the precise float (in seconds) when the sound ends.

---

### Rules

- Use the transcription to identify **specific physical actions or events** that require **sound effects** (e.g., "a door slams", "a car drives by", "a glass breaks").
- Use the image and transcription to identify **ambient or environmental sounds** that should play as **background**. These represent the constant atmosphere of the scene (e.g., rain, wind, traffic hum).
  - **If a sound is persistent or continuous throughout the scene**, such as rainfall, ocean waves, or a humming machine, it must be added as a **background sound**, not as a sound effect.
  - The background sound must reflect **all relevant constant elements** present in the scene. For example, if it's raining and there is distant thunder or city traffic, the background sound must combine these into one coherent ambient sound.
  - Background sounds should reflect the **overall environment** and **remain consistent** during the scene.
- You must generate **only one background sound**. It can last up to **22.0 seconds**, or match the full duration of the scene if appropriate.
- You may generate **up to 3 sound effects**. Each must:
  - Be based on a specific action mentioned in the transcription.
  - Last between **1.0 and 5.0 seconds**.
  - Be naturally timed to the moment it represents.
- **Do not include music in any sound**, including both background and sound effects.
- Spoken language (including dialogue and narration) must **not** be included.  
  - However, **non-verbal human sounds** (such as gasps, coughing, footsteps, distant crowd murmur) are allowed when clearly relevant.
- Do not include names or pronouns.

---

### Transcription  
{transcription or "This scene has no transcription. Generate only one ambient/environmental sound using the image."}


'''

    async def _generate_sound_effect_audio(self, description: str, start: float, end: float, audio_file_path: str) -> SoundEffectAudio:
        try:
            async with self.semaphore:
                duration = min(max(end-start, 0.5), 22)
                options = SoundEffectGenerationOptions(duration=duration)
                self.logger.info(f"Generating sound effect audio with description: {description}")
                audio_data = await exponential_backoff_call(self.tts.to_sound_effect, description, options)

                with open(audio_file_path, "wb") as f:
                    f.write(audio_data)

                self.logger.info(f"Saved sound effect audio file to {audio_file_path}")

                return SoundEffectAudio(
                    clip=AudioFileClip(audio_file_path).with_start(start),
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
                sound_effect_description.description,
                sound_effect_description.start_time,
                sound_effect_description.end_time,
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
