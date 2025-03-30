import logging
import asyncio
import os

from tts.tts import TTS, SpeechGenerationOptions
from script.script import Line
from story.story import StoryNode, Character
from audio.exceptions import AudioGenerationError

class AudioService:
    def __init__(self, tts: TTS, max_concurrent_requests: int = 2):
        self.tts = tts
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def _generate_and_save_line(self, language: str, characters: list[Character], line: Line, scene_id: str, line_index: int, output_dir: str) -> tuple[str, str, int]:
        try:
            async with self.semaphore:
                options = SpeechGenerationOptions()
                if line.type == "dialogue":
                    character = next((c for c in characters if c.name == line.character), None)
                    if not character.voice_id:
                        used_voices = set([character.voice_id for character in characters if character.voice_id])
                        character.voice_id = await self.tts.get_voice(language, used_voices, character)
                    options.voice = character.voice_id
                else:
                    options.voice = await self.tts.get_voice(language, [], None)

                audio_data = await self.tts.to_speech(line.line, options)
                
                file_path = os.path.join(output_dir, f"{scene_id}_{line_index}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                    
                return file_path, scene_id, line_index
                    
        except Exception as e:
            self.logger.error(f"Failed to generate {line.type} for scene {scene_id} line {line_index}: {str(e)}")
            raise AudioGenerationError(f"Failed to generate {line.type} for scene {scene_id} line {line_index}: {str(e)}")
        
    def _group_audio_paths_by_scene(self, audio_paths: list[tuple[str, str, int]]) -> dict[str, list[str]]:
        sorted_audio_paths = sorted(audio_paths, key=lambda x: (x[1], x[2]))

        scenes_lines_audio_paths = {}
        for file_path, scene_id, _ in sorted_audio_paths:
            if scene_id not in scenes_lines_audio_paths:
                scenes_lines_audio_paths[scene_id] = []
            scenes_lines_audio_paths[scene_id].append(file_path)
        return scenes_lines_audio_paths

    async def generate_scenes_lines(self, story_node: StoryNode, output_dir: str) -> dict[str, list[str]]:
        os.makedirs(output_dir, exist_ok=True)
        
        tasks = [
            self._generate_and_save_line(story_node.script.language, story_node.characters, line, scene_id, line_index, output_dir)
            for scene_id, line, line_index in ((scene.id, line, line_index) for scene in story_node.script.scenes for line_index, line in enumerate(scene.lines))
        ]
        audio_paths = await asyncio.gather(*tasks)
        
        return self._group_audio_paths_by_scene(audio_paths)
