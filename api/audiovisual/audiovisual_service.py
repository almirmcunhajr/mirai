import logging
import os
from typing import List, Optional
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

from script.script import Script
from visual.visual_service import VisualService
from audio.audio_service import AudioService

class AudioVisualService:
    def __init__(self, visual_service: VisualService, audio_service: AudioService):
        self.visual_service = visual_service
        self.audio_service = audio_service
        self.logger = logging.getLogger(__name__)

    def generate_video(self, script: Script, output_dir: str) -> Optional[str]:
        """
        Generates a video by composing images and audio for each frame in the script.
        
        Args:
            script (Script): The script containing frames to generate content for
            output_dir (str): Directory to save the generated files
            
        Returns:
            Optional[str]: Path to the generated video file, or None if generation failed
        """
        # Create directories for intermediate files
        images_dir = os.path.join(output_dir, "images")
        audio_dir = os.path.join(output_dir, "audio")
        os.makedirs(output_dir, exist_ok=True)

        # Generate images and audio
        image_paths = self.visual_service.generate_images(script, images_dir)
        narration_paths = self.audio_service.generate_narrations(script, audio_dir)

        # Check if we have all the required files
        if None in image_paths or None in narration_paths:
            self.logger.error("Some frames failed to generate, cannot create complete video")
            return None

        try:
            # Create video clips for each frame
            clips = []
            for image_path, narration_path in zip(image_paths, narration_paths):
                # Load audio to get its duration
                audio = AudioFileClip(narration_path)
                
                # Create image clip with same duration as audio
                image = ImageClip(image_path).set_duration(audio.duration)
                
                # Combine image and audio
                video_clip = image.set_audio(audio)
                clips.append(video_clip)

            # Concatenate all clips
            final_clip = concatenate_videoclips(clips)

            # Write the final video
            output_path = os.path.join(output_dir, "story.mp4")
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

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to generate video: {str(e)}")
            return None 