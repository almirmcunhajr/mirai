import logging
import asyncio
from typing import List
import os

from tts.tts import TTS
from script.script import Script, Frame
from audio.exceptions import AudioGenerationError

class AudioService:
    def __init__(self, tts: TTS, max_concurrent_requests: int = 2):
        self.tts = tts
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def _generate_and_save_narration(self, frame: Frame, i: int, output_dir: str) -> str:
        try:
            async with self.semaphore:
                audio_data = await self.tts.to_speech(frame.narration)
                
                file_path = os.path.join(output_dir, f"narration_{i+1}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                    
                return file_path
                    
        except Exception as e:
            self.logger.error(f"Failed to generate narration for frame {i+1}: {str(e)}")
            raise AudioGenerationError(f"Failed to generate narration for frame {i+1}: {str(e)}")

    async def generate_narrations(self, script: Script, output_dir: str) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        
        tasks = [
            self._generate_and_save_narration(frame, i, output_dir)
            for i, frame in enumerate(script.frames)
        ]
        audio_paths = await asyncio.gather(*tasks)
        return audio_paths 