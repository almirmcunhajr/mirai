import logging
import os
import tempfile
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips

from script.script import Script
from visual.visual_service import VisualService
from audio.audio_service import AudioService
from visual.exceptions import ImageGenerationError
from audio.exceptions import AudioGenerationError
from audiovisual.exceptions import VideoGenerationError

class AudioVisualService:
    def __init__(self, visual_service: VisualService, audio_service: AudioService):
        self.visual_service = visual_service
        self.audio_service = audio_service
        self.logger = logging.getLogger(__name__)

    def generate_video(self, script: Script, output_path: str) -> None:
        """
        Generates a video by composing images and audio for each frame in the script.
        
        Args:
            script (Script): The script containing frames to generate content for
            output_path (str): Path where the video should be saved
            
        Raises:
            VideoGenerationError: If video generation fails
        """
        # Create temporary directories for intermediate files
        temp_dir = tempfile.mkdtemp(dir=os.path.dirname(output_path))
        images_dir = os.path.join(temp_dir, "images")
        audio_dir = os.path.join(temp_dir, "audio")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        
        try:
            # Generate images and audio
            self.logger.info("Generating images...")
            image_paths = self.visual_service.generate_images(script, images_dir)
            self.logger.info(f"Generated {len(image_paths)} images")
            
            self.logger.info("Generating audio...")
            narration_paths = self.audio_service.generate_narrations(script, audio_dir)
            self.logger.info(f"Generated {len(narration_paths)} audio files")
            
            # Check if we have all the required files
            if None in image_paths or None in narration_paths:
                raise VideoGenerationError("Some frames failed to generate, cannot create complete video")
            
            # Create video clips for each frame
            self.logger.info("Creating video clips...")
            clips = []
            for i, (image_path, narration_path) in enumerate(zip(image_paths, narration_paths)):
                self.logger.info(f"Processing frame {i+1}/{len(image_paths)}")
                # Create audio clip
                audio = AudioFileClip(narration_path)

                # Create image clip
                image = ImageClip(image_path)
                
                # Combine image and audio
                video = image.with_duration(audio.duration).with_audio(audio)
                clips.append(video)
            
            # Concatenate all clips
            self.logger.info("Concatenating video clips...")
            final_clip = concatenate_videoclips(clips)
            
            # Write the final video
            self.logger.info(f"Writing final video to {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Close all clips to free up resources
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
            # Clean up temporary files
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                self.logger.info("Cleaned up temporary files") 