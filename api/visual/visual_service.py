import logging
import asyncio
import base64

from tti.tti import TTI
from ttt.ttt import TTT, Chat, ChatOptions
from script.script import Scene
from visual.exceptions import ImageGenerationError
from story.story import Style
from visual.visual import Visual

from moviepy.video.VideoClip import ImageClip

class VisualService:
    def __init__(self, tti: TTI, ttt: TTT, max_concurrent_requests: int = 8):
        self.tti = tti
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def _get_decription_simplification_prompt(self, description: str) -> str:
        return f''''Improve the following description so it can be used as a high-quality text-to-image prompt. Keep it under 400 words, using plain and clear English:
{description}

**Do not add any new elements or remove important visual features**
'''
    
    async def _simplify_scene_description(self, description: str) -> str:
        prompt = self._get_decription_simplification_prompt(description)
        chat = Chat()
        chat.add_user_message(prompt)
        return await self.ttt.chat(chat, ChatOptions())

    async def _get_image_generation_prompt(self, scene: Scene, style: Style) -> str:
        simplified_description = await self._simplify_scene_description(scene.visual_description)
        return f'''In a {style} style scene. {simplified_description}'''
    
    async def generate_scene_visual(self, scene: Scene, style: Style, image_file_path: str) -> Visual:
        try:
            async with self.semaphore:
                prompt = await self._get_image_generation_prompt(scene, style)

                self.logger.info(f"Generating image for scene {scene.id} with prompt: {prompt}")
                base64_image = await self.tti.to_image(prompt)
                if not base64_image:
                    raise ImageGenerationError("Empty response from TTI")
                
                with open(image_file_path, "wb") as f:
                    f.write(base64.b64decode(base64_image))
                
                self.logger.info(f"Saved image file to {image_file_path}")

                return Visual(
                    clip=ImageClip(image_file_path),
                    base64_image=base64_image
                )
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate image: {str(e)}")
