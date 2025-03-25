import logging
import os
import tempfile
import asyncio
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips

from script.script import Script
from visual.visual_service import VisualService
from story.story import Style
from audio.audio_service import AudioService
from visual.exceptions import ImageGenerationError
from audio.exceptions import AudioGenerationError
from audiovisual.exceptions import VideoGenerationError

class AudioVisualService:
    def __init__(self, visual_service: VisualService, audio_service: AudioService):
        self.visual_service = visual_service
        self.audio_service = audio_service
        self.logger = logging.getLogger(__name__)

    async def generate_video(self, script: Script, style: Style, output_path: str) -> None:
        temp_dir = tempfile.mkdtemp(dir=os.path.dirname(output_path))
        images_dir = os.path.join(temp_dir, "images")
        audio_dir = os.path.join(temp_dir, "audio")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        
        try:
            self.logger.info("Starting parallel generation of images and audio...")
            image_paths, narration_paths = await asyncio.gather(
                self.visual_service.generate_frames(script, images_dir, style),
                self.audio_service.generate_narrations(script, audio_dir)
            )
            self.logger.info(f"Generated {len(image_paths)} images and {len(narration_paths)} audio files")
            
            if None in image_paths or None in narration_paths:
                raise VideoGenerationError("Some frames failed to generate, cannot create complete video")
            
            self.logger.info("Creating video clips...")
            clips = []
            for i, (image_path, narration_path) in enumerate(zip(image_paths, narration_paths)):
                self.logger.info(f"Processing frame {i+1}/{len(image_paths)}")
                audio = AudioFileClip(narration_path)

                image = ImageClip(image_path)
                
                video = image.with_duration(audio.duration).with_audio(audio)
                clips.append(video)
            
            self.logger.info("Concatenating video clips...")
            final_clip = concatenate_videoclips(clips)
            
            self.logger.info(f"Writing final video to {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            final_clip.close()
            for clip in clips:
                clip.close()
                
            self.logger.info("Video generation completed successfully")
            
        except (ImageGenerationError, AudioGenerationError) as e:
            self.logger.error(f"Failed to generate video: {str(e)}", exc_info=True)
            raise VideoGenerationError(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error during video generation: {str(e)}", exc_info=True)
            raise VideoGenerationError(f"Unexpected error during video generation: {str(e)}")
        finally:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                self.logger.info("Cleaned up temporary files") 