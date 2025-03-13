import json
import re
import logging
from typing import List

from facade.chatbot import Chatbot
from script.script import Script, PathNode
from common.genre import Genre
from utils import validate_language

from pydantic import ValidationError

class InvalidLanguageError(Exception):
    """Raised when an invalid language code is provided."""
    pass

class InvalidChatBotResponse(Exception):
    """Raised when the chatbot response is invalid."""
    pass

class ScriptService:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot
        self.logger = logging.getLogger(__name__)

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from the response, handling both direct JSON and code blocks."""
        try:
            # Try parsing the response directly first
            return json.loads(response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from code blocks
            json_block_regex = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
            match = json_block_regex.search(response)
            if not match:
                raise InvalidChatBotResponse(response)
            return json.loads(match.group(1))

    async def generate(self, genre: Genre, language_code: str, path: List[PathNode] = []) -> Script:
        """
        Generate a narrative script in the specified genre and language.
        
        Args:
            genre (Genre): The genre of the narrative
            language_code (str): The ISO 639-1 or ISO 639-2 language code (e.g., 'en', 'eng', 'pt', 'por')
            path (List[PathNode]): List of previous script-decision pairs in the story path
            
        Returns:
            Script: The generated script
            
        Raises:
            InvalidLanguageError: If the language code is invalid
            InvalidChatBotResponse: If the chatbot response is invalid
        """
        # Validate language code
        language = validate_language(language_code)
        if not language:
            raise InvalidLanguageError(f"Invalid language code: {language_code}")

        prompt = f'''
        Generate a {genre.value} narrative in {language} up to a crucial decision moment. The story should be engaging, with a clear progression of events, culminating in a meaningful choice for the protagonist.

        The narrative should be structured into frames, each representing a moment or scene, with vivid and consistent details about characters and the environment. Each frame should precisely describe visual attributes, emotions, and postures of the characters, as well as lighting, weather, sounds, and objects in the scene, ensuring that characteristics remain uniform throughout the narrative.

        The exhaustive repetition of visual and narrative details must be maintained in all frames to ensure coherence in image generation. Subtle changes, such as alterations in expression, posture, or object positioning, should be explicitly described to ensure logical continuity between frames.

        IMPORTANT: Keep the descriptions family-friendly and avoid any graphic violence, gore, or disturbing content. Focus on the beauty, wonder, and magic of the fantasy world.

        The response should be a JSON that will be validated against the following schema:
        ```
        {{
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {{
                "title": {{
                    "type": "string",
                    "description": "The title of the narrative."
                }},
                "frames": {{
                    "type": "array",
                    "description": "A list of objects representing each frame of the narrative.",
                    "items": {{
                        "type": "object",
                        "properties": {{
                            "narration": {{
                                "type": "string",
                                "description": "A narrative text describing the events of the frame."
                            }},
                            "description": {{
                                "type": "string",
                                "description": "An extremely detailed description of the characters and the environment, formatted as a prompt for generating an illustrative image."
                            }}
                        }},
                        "required": ["narration", "description"]
                    }}
                }},
                "decisions": {{
                    "type": "array",
                    "description": "A list of possible choices for the protagonist at the final moment of the narrative.",
                    "items": {{
                        "type": "string"
                    }}
                }}
            }},
            "required": ["title", "frames", "decisions"]
        }}
        ```
        '''
        if path:
            prompt = f'''
            Continuing the narrative, describe the unfolding events up to the next crucial decision moment or the story's conclusion. The progression of events should be clear, maintaining immersion and ensuring an impactful conclusion or a new significant choice for the protagonist.

            The narrative should be structured into frames, each representing a moment or scene, with exhaustive and consistent details about characters and the environment. Each frame should precisely describe visual attributes, emotions, and postures of the characters, as well as lighting, weather, sounds, and objects in the scene, ensuring that characteristics remain uniform throughout the narrative.

            The detailed repetition of visual and narrative elements must be maintained in all frames to ensure coherence in image generation. Subtle changes, such as variations in expression, posture, or object displacement, should be explicitly described to ensure logical continuity between frames.

            IMPORTANT: Keep the descriptions family-friendly and avoid any graphic violence, gore, or disturbing content. Focus on the beauty, wonder, and magic of the fantasy world.

            The response should be a JSON that will be validated against the following schema:
            ```
            {{
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {{
                    "title": {{
                        "type": "string",
                        "description": "The title of the narrative."
                    }},
                    "frames": {{
                        "type": "array",
                        "description": "A list of objects representing each frame of the narrative.",
                        "items": {{
                            "type": "object",
                            "properties": {{
                                "narration": {{
                                    "type": "string",
                                    "description": "A narrative text describing the events of the frame."
                                }},
                                "description": {{
                                    "type": "string",
                                    "description": "An extremely detailed description of the characters and the environment, formatted as a prompt for generating an illustrative image."
                                }}
                            }},
                            "required": ["narration", "description"]
                        }}
                    }},
                    "decisions": {{
                        "type": "array",
                        "description": "A list of possible choices for the protagonist at the final moment of the narrative.",
                        "items": {{
                            "type": "string"
                        }}
                    }}
                }},
                "required": ["title", "frames", "decisions"]
            }}
            ```

            This narrative genre is {genre.value} and the language is {language}.

            Below is the current path up to this point, listed in chronological order. Each element contains the previously generated response in the script field and the corresponding decision in the decision field:
            ```json
            {json.dumps([node.model_dump() for node in path])}
            ```
            '''
        response = await self.chatbot.generate_text(prompt)

        try:
            script_dict = self._parse_json_response(response)
            return Script(**script_dict)
        except (json.JSONDecodeError, ValidationError):
            raise InvalidChatBotResponse(response)
