import logging
import asyncio
import aiohttp
import os
import base64
from typing import List

from tti.tti import TTI
from script.script import Script, Scene
from visual.exceptions import ImageGenerationError
from story.story import Style

class VisualService:
    def __init__(self, tti: TTI, max_concurrent_requests: int = 8):
        self.tti = tti
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def _get_image_generation_prompt(self, scene: Scene, style: Style) -> str:
        return f'''Generate a scene in **{style}** style with the following description:
{scene.description}
'''

    async def _generate_and_save_frame(self, scene: Scene, image_file_path: str, style: Style) -> str:
        try:
            async with self.semaphore:
                base64_image = await self.tti.to_image(self._get_image_generation_prompt(scene, style))
                if not base64_image:
                    raise ImageGenerationError("Empty response from TTI")
                
                with open(image_file_path, "wb") as f:
                    f.write(base64.b64decode(base64_image))
                
                return image_file_path
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate image: {str(e)}")

    async def generate_frames(self, script: Script, output_dir: str, style: Style) -> List[str]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._generate_and_save_frame(scene, os.path.join(output_dir, f"frame_{i+1}.png"), style)
                for i, scene in enumerate(script.scenes)
            ]
            
            image_paths = await asyncio.gather(*tasks)
            return image_paths

class InvalidChatBotResponse(Exception):
    pass