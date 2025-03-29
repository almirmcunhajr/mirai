import logging
import os
import tempfile
import asyncio
import shutil
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.audio.AudioClip import concatenate_audioclips

from visual.visual_service import VisualService
from story.story import Style
from audio.audio_service import AudioService
from visual.exceptions import ImageGenerationError
from audio.exceptions import AudioGenerationError
from audiovisual.exceptions import VideoGenerationError
from story.story import StoryNode

class AudioVisualService:
    def __init__(self, visual_service: VisualService, audio_service: AudioService):
        self.visual_service = visual_service
        self.audio_service = audio_service
        self.logger = logging.getLogger(__name__)

    async def generate_video(self, story_node: StoryNode, style: Style, output_path: str) -> str:
        temp_dir = tempfile.mkdtemp(dir=os.path.dirname(output_path))
        images_dir = os.path.join(temp_dir, "images")
        audio_dir = os.path.join(temp_dir, "audio")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)

        script = story_node.script
        try:
            self.logger.info("Starting parallel generation of images and audio...")
            scenes_images_paths, scenes_lines_audio_paths = await asyncio.gather(
                self.visual_service.generate_scenes_images(script, images_dir, style),
                self.audio_service.generate_scenes_lines(script, audio_dir)
            )

            self.logger.info("Generating video clips...")
            scenes_clips = []
            for scene in script.scenes:
                self.logger.info(f"Generating video clip for scene {scene.id}")

                image_path = scenes_images_paths[scene.id]
                lines_paths = scenes_lines_audio_paths[scene.id]

                image_clip = ImageClip(image_path)
                concatenated_audio = concatenate_audioclips([AudioFileClip(line_path) for line_path in lines_paths])
                scene_clip = image_clip.with_duration(concatenated_audio.duration).with_audio(concatenated_audio)
                scenes_clips.append(scene_clip)

            self.logger.info("Concatenating video clips...")
            final_clip = concatenate_videoclips(scenes_clips)
            
            self.logger.info(f"Writing final video to {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            final_clip.close()
            for scene_clip in scenes_clips:
                scene_clip.close()
                
            self.logger.info("Video generation completed successfully")
        except (ImageGenerationError, AudioGenerationError) as e:
            self.logger.error(f"Failed to generate video: {str(e)}", exc_info=True)
            raise VideoGenerationError(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error during video generation: {str(e)}", exc_info=True)
            raise VideoGenerationError(f"Unexpected error during video generation: {str(e)}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                self.logger.info("Cleaned up temporary files") 