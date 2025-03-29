import logging

from ttt.ttt import TTT, ChatOptions, Chat
from script.script import Script, Scene, Ending, Character
from common.genre import Genre
from common.base_model_no_extra import BaseModelNoExtra
from utils import validate_language


class InvalidLanguageError(Exception):
    """Raised when an invalid language code is provided."""
    pass

class InvalidChatBotResponse(Exception):
    """Raised when the chatbot response is invalid."""
    pass

class ScriptResponse(BaseModelNoExtra):
    title: str
    genre: Genre
    language: str
    scenes: list[Scene]
    ending: Ending

class CharacterResponse(BaseModelNoExtra):
    name: str
    age: int
    gender: str

class CharactersResponse(BaseModelNoExtra):
    characters: list[CharacterResponse]

class ScriptService:
    def __init__(self, ttt: TTT):
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)

    def _get_narrative_generation_message(self, genre: Genre, language: str) -> str:
        return f'''Generate a {genre.value} narrative in {language} up to a decision moment. 
The story should be engaging, with a clear development of the characters and progression of events, culminating in a choice for the protagonist.
'''
    
    def _get_script_generation_message(self) -> str:
        return f'''Convert the story into a structured JSON document, formatted as a cinematic screenplay.

I will use this output with two models:

A text-to-image model like DALL·E, which does not retain context between prompts

A text-to-speech and video generation system, which must follow the exact order of narration and dialogue lines

Please follow these instructions **carefully**:

- Each scene must include a visual_description field that is a single, complete, and self-contained string, suitable for generating one image.

- ⚠️ VERY IMPORTANT: **DO NOT** use **PRONOUNS**, **CHARACTER NAMES**, or **VAGUE REFERENCES** in the visual_description. Always **FULLY DESCRIBE**:
    Characters: **ALWAYS** include age, gender, skin tone, hair type and color, clothing (style and color), facial expression, posture, and any distinctive visual features (e.g., glasses, scars).
    Locations: describe **FULLY** in **EVERY** scene, even if previously shown.

- Each scene must also include a lines array representing all spoken and narrated content in sequential order. Each item in the array must follow this structure:
    - type: indicates whether the line is a "dialogue" or a "narration".
    - character: the speaker's name; use "Narrator" only for general narration (not internal monologue).
    - line: the actual spoken or narrated content.

All dialogue and narration lines must be written in natural, expressive language, using names, pronouns, emotions, and realistic tone — as in a real screenplay.

The final JSON must include:
- title, genre, language
- A list of scenes, each containing:
    - id: e.g., "1"
    - visual_description: one complete, self-contained string
    - lines: ordered array of narration and dialogue objects
- An ending object with:
    - type: "decision" (for decision points) or "end" (for story conclusions)
    - description: a narration-ready summary of the final moment or situation
        '''
    def _get_characteres_message(self) -> str:
        return f'''Based on the story or script, extract the list of characters and return them as a JSON object.

The value for each character must be an object containing:
    - name: the character's name
    - age: approximate age (as an integer)
    - gender: "male", "female", or "other" if applicable

⚠️ The character names used as keys must **exactly match** the names used in the "character" fields inside the lines array of the script (both for dialogue and narration). This ensures voice-matching works properly later.

Only include characters who speak or narrate in the script.
Do not include "Narrator" — it is a system voice, not a character.
'''
    
    def _get_decision_message(self, decision: str) -> str:
        return f'''I decided to "{decision}".'''
    
    async def generate(self, chat: Chat, genre: Genre = None, language_code: str = None, decision: str = None) -> Script:
        if language_code and not validate_language(language_code):
            raise InvalidLanguageError(f"Invalid language code: {language_code}")
        
        if not decision:
            message = self._get_narrative_generation_message(genre, language_code)
            chat.add_user_message(message)

            chat_options = ChatOptions()
            narrative = await self.ttt.chat(chat, chat_options)
            chat.add_assistant_response(narrative)

            message = self._get_script_generation_message()
            chat.add_user_message(message)
        else:
            message = self._get_decision_message(decision)
            chat.add_user_message(message)

        chat_options = ChatOptions(response_format=ScriptResponse)
        script_response: ScriptResponse = await self.ttt.chat(chat, chat_options)
        chat.add_assistant_response(script_response.model_dump_json())

        message = self._get_characteres_message()
        chat.add_user_message(message)

        chat_options = ChatOptions(response_format=CharactersResponse)
        characters_response: CharactersResponse = await self.ttt.chat(chat, chat_options)
        chat.add_assistant_response(characters_response.model_dump_json())

        return Script(
            title=script_response.title,
            genre=script_response.genre,
            language=script_response.language,
            scenes=script_response.scenes,
            characters=[Character(name=character.name, age=character.age, gender=character.gender) for character in characters_response.characters],
            ending=script_response.ending
        )
