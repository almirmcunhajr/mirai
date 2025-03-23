import logging
import asyncio
import aiohttp
import os
import base64
from typing import List

from tti.tti import TTI
from script.script import Script
from visual.exceptions import ImageGenerationError

class VisualService:
    def __init__(self, tti: TTI, max_concurrent_requests: int = 8):
        self.tti = tti
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def _generate_and_save_frame(self, frame, i: int, output_dir: str, session) -> str:
        """Generate and save a single frame."""
        try:
            async with self.semaphore:
                base64_image = await self.tti.to_image(frame.description)
                
                if not base64_image:
                    raise ImageGenerationError(f"No image generated for frame {i+1}")
                
                file_path = os.path.join(output_dir, f"frame_{i+1}.png")
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(base64_image))
                
                return file_path
        except Exception as e:
            self.logger.error(f"Failed to generate/save image for frame {i+1}: {str(e)}")
            raise ImageGenerationError(f"Failed to generate/save image for frame {i+1}: {str(e)}")

    async def generate_frames(self, script: Script, output_dir: str) -> List[str]:
        """Generate frames for a script in parallel."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._generate_and_save_frame(frame, i, output_dir, session)
                for i, frame in enumerate(script.frames)
            ]
            
            image_paths = await asyncio.gather(*tasks)
            return image_paths

class InvalidChatBotResponse(Exception):
    pass 