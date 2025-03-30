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
        return f'''Generate a scene in {style} style with the following description:
{scene.visual_description}

Make sure the characteres are naturaly and coherently acting.
'''

    async def _generate_and_save_scene(self, scene: Scene, image_file_path: str, style: Style) -> tuple[str, str]:
        try:
            async with self.semaphore:
                base64_image = await self.tti.to_image(self._get_image_generation_prompt(scene, style))
                if not base64_image:
                    raise ImageGenerationError("Empty response from TTI")
                
                with open(image_file_path, "wb") as f:
                    f.write(base64.b64decode(base64_image))
                
                return image_file_path, scene.id
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate image: {str(e)}")

    async def generate_scenes_images(self, script: Script, output_dir: str, style: Style) -> dict[str, str]:
        async with aiohttp.ClientSession():
            tasks = [
                self._generate_and_save_scene(scene, os.path.join(output_dir, f"scene_{i+1}.png"), style)
                for i, scene in enumerate(script.scenes)
            ]
            
            image_paths = await asyncio.gather(*tasks)
            return {scene_id: image_path for image_path, scene_id in image_paths}
