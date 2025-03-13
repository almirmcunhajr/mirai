import logging
from typing import List
import os
import requests

from facade.tti import TTI
from script.script import Script

class VisualService:
    def __init__(self, tti: TTI):
        self.tti = tti
        self.logger = logging.getLogger(__name__)

    def generate_images(self, script: Script, output_dir: str) -> List[str]:
        """
        Generates images for each frame in the script using the TTI service.
        
        Args:
            script (Script): The script containing frames to generate images for
            output_dir (str): Directory to save the generated image files
            
        Returns:
            List[str]: List of paths to the generated image files
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        image_paths = []
        
        for i, frame in enumerate(script.frames):
            try:
                # Generate image URL
                url = self.tti.generate_image(frame.description)
                
                if url:
                    # Download and save the image
                    response = requests.get(url)
                    response.raise_for_status()
                    
                    file_path = os.path.join(output_dir, f"frame_{i+1}.png")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                        
                    image_paths.append(file_path)
                else:
                    self.logger.error(f"No URL generated for frame {i+1}")
                    image_paths.append(None)
                    
            except Exception as e:
                self.logger.error(f"Failed to generate/save image for frame {i+1}: {str(e)}")
                image_paths.append(None)
                
        return image_paths

class InvalidChatBotResponse(Exception):
    pass 