import logging
from typing import List
import os

from facade.tts import TTS
from script.script import Script
from audio.exceptions import AudioGenerationError

class AudioService:
    def __init__(self, tts: TTS):
        self.tts = tts
        self.logger = logging.getLogger(__name__)

    def generate_narrations(self, script: Script, output_dir: str) -> List[str]:
        """
        Generates audio narrations for each frame in the script using text-to-speech.
        
        Args:
            script (Script): The script containing frames to generate narrations for
            output_dir (str): Directory to save the generated audio files
            
        Returns:
            List[str]: List of paths to the generated audio files
            
        Raises:
            AudioGenerationError: If audio generation or saving fails
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        audio_paths = []
        
        for i, frame in enumerate(script.frames):
            try:
                # Generate audio for the frame's narration
                audio_data = self.tts.generate_speech(frame.narration)
                
                # Save audio to file
                file_path = os.path.join(output_dir, f"narration_{i+1}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                    
                audio_paths.append(file_path)
                
            except Exception as e:
                self.logger.error(f"Failed to generate narration for frame {i+1}: {str(e)}")
                raise AudioGenerationError(f"Failed to generate narration for frame {i+1}: {str(e)}")
                
        return audio_paths 