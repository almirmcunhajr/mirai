import json
import re
import logging

from facade.chatbot import Chatbot
from script.script import Script
from api.common.genre import Genre
from api.common.idiom import Idiom
from script.branch import Branch

from pydantic import ValidationError

class ScriptService:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot
        self.logger = logging.getLogger(__name__)

    def generate(self, genre: Genre, idiom: Idiom, path:list[Branch] = []) -> dict:
        prompt = f''' 
        Generate a {genre.value} narrative in {idiom.value} up to a crucial decision moment. The story should be engaging, with a clear progression of events, culminating in a meaningful choice for the protagonist.

        The narrative should be structured into frames, each representing a moment or scene, with vivid and consistent details about characters and the environment. Each frame should precisely describe visual attributes, emotions, and postures of the characters, as well as lighting, weather, sounds, and objects in the scene, ensuring that characteristics remain uniform throughout the narrative.

        The exhaustive repetition of visual and narrative details must be maintained in all frames to ensure coherence in image generation. Subtle changes, such as alterations in expression, posture, or object positioning, should be explicitly described to ensure logical continuity between frames.

        The response should be in JSON format and conform to the following JSON schema:
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

            The response should be in JSON format and conform to the following JSON schema:
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

            This narrative genre is {genre.value} and the idiom is {idiom.value}.

            Below is the current path up to this point, listed in chronological order. Each element contains the previously generated response in the script field and the corresponding decision in the decision field:
            ```json
            {json.dumps(path)}
            ```
            '''
        response = self.chatbot.get_response(prompt)

        json_block_regex = re.compile(r'```json([\s\S]*?)```')
        match = json_block_regex.search(response)
        if not match:
            raise InvalidChatBotResponse(response)
        json_response = match.group(1)

        try:
            script_dict = json.loads(json_response)
            script = Script(**script_dict)
            return script.model_dump()
        except json.JSONDecodeError:
            raise InvalidChatBotResponse(response)
        except ValidationError:
            raise InvalidChatBotResponse(response)
        
class InvalidChatBotResponse(Exception):
    pass
