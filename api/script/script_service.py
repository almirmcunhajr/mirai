import logging
from pydantic import BaseModel
import re
from functools import partial

from ttt.ttt import TTT, ChatOptions, Chat
from script.script import Script, Scene
from story.story import Subject
from common.genre import Genre
from utils import validate_language


class InvalidLanguageError(Exception):
    """Raised when an invalid language code is provided."""
    pass

class InvalidChatBotResponse(Exception):
    """Raised when the chatbot response is invalid."""
    pass

class ScriptResponse(BaseModel):
    title: str
    scenes: list[Scene]
    references: list[Subject]

class ScriptService:
    def __init__(self, ttt: TTT):
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)
        self.chat_options = ChatOptions(response_format=ScriptResponse)

    def _get_script_generation_initial_message(self, genre: Genre, language: str) -> str:
        return f'''Generate a {genre.value} narrative in {language} up to a decision moment. The story should be engaging, with a clear development of the characters and progression of events, culminating in a choice for the protagonist.

The narrative should be structured into scenes. Each scene should contain the narration of the scene, and detailed **visual aspects** and **acting** in the description. 
In all scenes description make sure to reference all characters, objects, places, etc. using only an id in the format #<number>, starting from 1, and incrementing by 1.
Also, return a list of the references, with their detailed visual aspects and their name.

Make sure the descriptions have a *maximum length of 3500 characteres*, and are **family-friendly**, avoiding any graphic violence, gore, disturbing content,etc.

The narration should not include any ids, it will be used later by a text to speech service to create an audio for the narration.

IMPORTANT: Make sure to **reference all characters, objects, places, etc. in all scenes**. And make sure to decribe the characters in great details, including a dense visual description of the body, face, hair, clothes, etc.

# Descriptions examples
## Description example for scene 1:
The scene starts in #0 (In this example, 0 is a place, and you should describe 0 in details in the references list). #1 (In this example, #1 is a character, and you should describe #1 in details in the references list) is doing something and got #2 (In this example, #2 is an object, and you should describe #2 in details in the references list)...

## Description example for scene 2:
In #0 (In this example, is the same place referenced by 0 in the previous scene), #1 is doing another thing, and meet #3 (In this example, #3 is another character, and you should describe #3 in details in the references list)...

## Description example for scene 3:
In #4 (In this example, #4 is another place, and you should describe #4 in details in the references list)...

...
## Description example for scene N:
...
'''
    def _get_already_created_references_message(self, references: list[Subject]) -> str:
        if len(references) == 0:
            return ''
        return f'''\nAttend to the following already created references:
{'\n'.join([f'#{i+1}:\nName:{reference.name}\nDescription:{reference.description}\n' for i, reference in enumerate(references)])}
'''

    def _get_script_generation_decision_message(self, decision: str, references: list[Subject]) -> str:
        return f'''I decided to "{decision}".

Continue the narrative, describe the unfolding events up to the next decision moment or the story's conclusion. The progression of events should be clear, maintaining immersion and ensuring a new choice for the protagonist or a impactful conclusion.

Continue the references from the previous scenes. That is, if the previous scenes generated references #0, #1, #2, #3, #4, then the new created references should continue from #5, and you should return references from #5 in the list. You can still reference the past references, but you should not return them in the list.
{self._get_already_created_references_message(references)}
# Descriptions examples
## Description example for scene N + 1:
In #0 (In this example, #0 is reference from the last responses, and you should not return it in the list), #5 is doing something (In this example, #5 is a new reference, and you should describe #5 in details in the references list)...
...
'''

    def _parse_script_response(self, response: ScriptResponse) -> Script:
        def replace_id(substituted: dict[int, int], match):
            id = int(match.group(1))-1
            reference = response.references[id]
            if id not in substituted:
                sub = f'{reference.name} ({reference.description})'
            else:
                sub = reference.name
            substituted[id] = 1
            return sub

        for scene in response.scenes:
            substituted = {}
            scene.description = re.sub(r'#(\d+)', partial(replace_id, substituted), scene.description)

        return Script(
            title=response.title,
            scenes=response.scenes,
            subjects=response.references
        )
    
    async def generate(self, chat: Chat = Chat(), subjects: list[Subject] = [], genre: Genre = None, language_code: str = None, decision: str = None) -> tuple[Script, list[Subject], Chat]:
        language = validate_language(language_code)
        if not language:
            raise InvalidLanguageError(f"Invalid language code: {language_code}")

        message = self._get_script_generation_initial_message(genre, language)
        if decision:
            message = self._get_script_generation_decision_message(decision, subjects)

        chat.add_user_message(message)
        response: ScriptResponse = await self.ttt.chat(chat, self.chat_options)
        chat.add_assistant_response(response.model_dump_json())

        response.references = subjects + response.references
        
        script = self._parse_script_response(response)

        return script, response.references, chat