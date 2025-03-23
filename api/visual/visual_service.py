import logging
import asyncio
import aiohttp
import os
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
            # Use semaphore to limit concurrent requests
            async with self.semaphore:
                # Generate image URL
                url = await self.tti.generate_image(frame.description)
                
                if not url:
                    raise ImageGenerationError(f"No URL generated for frame {i+1}")
                
                # Download and save the image
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    
                    file_path = os.path.join(output_dir, f"frame_{i+1}.png")
                    with open(file_path, "wb") as f:
                        f.write(content)
                        
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
            
            # Execute all tasks concurrently and gather results
            image_paths = await asyncio.gather(*tasks)
            return image_paths

class InvalidChatBotResponse(Exception):
    pass 