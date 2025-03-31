import logging
import os
import tempfile
import asyncio

from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut, MultiplyVolume

from visual.visual_service import VisualService
from story.story import Style, Subject
from script.script import Scene
from audio.audio_service import AudioService, LineAudio
from visual.exceptions import ImageGenerationError
from audio.exceptions import AudioGenerationError
from audiovisual.exceptions import VideoGenerationError
from story.story import StoryNode

class AudioVisualService:
    def __init__(self, visual_service: VisualService, audio_service: AudioService):
        self.visual_service = visual_service
        self.audio_service = audio_service
        self.logger = logging.getLogger(__name__)

    def _get_audio_fade_duration(self, clip: AudioFileClip) -> float:
        return max(min(0.1 * clip.duration, 2), 0.2)

    async def _generate_sound_effects_audio_clip(self, lines_audios: list[LineAudio], scene_base64_image: str, output_path: str) -> CompositeAudioClip:
        os.makedirs(output_path, exist_ok=True)
        sound_effects_audios = await self.audio_service.generate_sound_effects_audios(lines_audios, scene_base64_image, output_path)
        return CompositeAudioClip([audio.clip.with_effects([
            MultiplyVolume(0.8), 
            AudioFadeIn(self._get_audio_fade_duration(audio.clip)), 
            AudioFadeOut(self._get_audio_fade_duration(audio.clip))
        ]) for audio in sound_effects_audios])

    async def _generate_scene_lines_audio_clip(self, scene: Scene, language: str, subjects: dict[str, Subject], output_path: str) -> tuple[CompositeAudioClip, list[LineAudio]]:
        os.makedirs(output_path, exist_ok=True)
        lines_tasks = [
            self.audio_service.generate_line_audio(line, language, subjects, os.path.join(output_path, f"{scene.id}_{i}.mp3"))
            for i, line in enumerate(scene.lines)
        ]
        lines_audio = await asyncio.gather(*lines_tasks)

        last_line_end = 0
        for line_audio in lines_audio:
            line_audio.clip = line_audio.clip.with_start(last_line_end)
            last_line_end = last_line_end + line_audio.clip.duration

        return CompositeAudioClip([line_audio.clip for line_audio in lines_audio]), lines_audio
    
    async def _generate_scene_visual_clip(self, scene: Scene, style: Style, output_path: str) -> tuple[ImageClip, str]:
        os.makedirs(output_path, exist_ok=True)
        image_path = os.path.join(output_path, f"{scene.id}.png")
        visual = await self.visual_service.generate_scene_visual(scene, style, image_path)
        return visual.clip, visual.base64_image
    
    async def _generate_scene_clip(self, scene: Scene, language: str, style: Style, subjects: dict[str, Subject], output_path: str) -> ImageClip:
        (visual_clip, scene_base64_image), (lies_audio_clip, lines_audio) =  await asyncio.gather(
            self._generate_scene_visual_clip(scene, style, os.path.join(output_path, "images")),
            self._generate_scene_lines_audio_clip(scene, language, subjects, os.path.join(output_path, "audio"))
        )
        sound_effects_audio_clip = await self._generate_sound_effects_audio_clip(lines_audio, scene_base64_image, os.path.join(output_path, "audio"))

        audio_clip = CompositeAudioClip([lies_audio_clip, sound_effects_audio_clip])

        return visual_clip.with_duration(audio_clip.duration).with_audio(audio_clip)

    async def generate_video(self, story_node: StoryNode, style: Style, output_path: str) -> str:
        temp_dir = tempfile.mkdtemp(dir=os.path.dirname(output_path))

        script = story_node.script
        try:
            self.logger.info("Generating scenes clips...")
            tasks = [
                self._generate_scene_clip(scene, script.language, style, story_node.subjects, temp_dir)
                for scene in script.scenes
            ]
            scenes_clips = await asyncio.gather(*tasks)

            self.logger.info("Concatenating scenes clips...")
            video = concatenate_videoclips(scenes_clips)
            
            self.logger.info(f"Writing final video to {output_path}")
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='mp3'
            )
            video.close()
            for scene_clip in scenes_clips:
                scene_clip.close()
                
            self.logger.info("Video generation completed successfully")
        except (ImageGenerationError, AudioGenerationError) as e:
            self.logger.error(f"Failed to generate video: {str(e)}", exc_info=True)
            raise VideoGenerationError(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error during video generation: {str(e)}", exc_info=True)
            raise VideoGenerationError(f"Unexpected error during video generation: {str(e)}")
