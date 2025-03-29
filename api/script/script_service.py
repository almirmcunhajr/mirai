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
 The story should be engaging, with a clear development of the characters progression of events, and complex dialogs, culminating in a choice for the protagonist.
'''
    
    def _get_script_generation_message(self) -> str:
        return f'''Convert the story into a structured JSON document, formatted as a cinematic screenplay.

This output will be used with two separate AI systems:

1. A **text-to-image model** like DALL·E, which does **not retain context between prompts**.
2. A **text-to-speech and video generation system**, which must follow the **exact order** of narration and dialogue.

---

## ⚠️ Follow these instructions with absolute precision:

### 🎬 Output format:

Return a **valid JSON object** with the following structure:

- `title`: string  
- `genre`: string  
- `language`: string (e.g., "Portuguese" or "English")  
- `scenes`: array of scene objects, each containing:
  - `id`: string (e.g., `"1"`, `"2"`)
  - `visual_description`: string — see strict rules below
  - `lines`: array of objects with:
    - `type`: `"dialogue"` or `"narration"`
    - `character`: name of the speaker (use `"Narrator"` only for general narration)
    - `line`: the actual spoken or narrated content
- `ending`: object with:
  - `type`: `"decision"` or `"end"`
  - `description`: a narration-ready summary of the final moment

---

### 📸 `visual_description` rules (STRICT AND NON-NEGOTIABLE):

This field must be a **single, complete, and self-contained string**, describing the scene **as if no prior context exists**.

#### ❌ NEVER USE:
- Pronouns (e.g., “he”, “she”, “they”, “his”, “her”)
- Character names (e.g., “Lucas”, “Maria”)
- Vague references (e.g., “the young woman”, “the couple”, “the house”, “the same violin player”)

#### ✅ ALWAYS:
- Fully re-describe **every character**, **every location**, and **every object**, **from scratch**, in **every scene**, even if they have appeared before.

---

#### Character descriptions must include:
> Age range, gender, skin tone, hair type and color, facial expression, posture, clothing (style and color), and any distinctive features (e.g., scars, glasses, tattoos)

#### Location descriptions must include:
> Interior or exterior, architecture, visible furniture or objects, lighting, time of day, weather (if applicable), atmosphere and mood

> 💡 Each `visual_description` must stand alone — it should be enough to generate a full image without relying on any previous scenes.

---

### 🎭 `lines` rules:

Each scene must include an array called `lines`, in **sequential order**, containing both dialogue and narration.

Each line must be an object with:
- `type`: `"dialogue"` or `"narration"`
- `character`: speaker's name  
  - Use `"Narrator"` only for general exposition or scene-setting narration
- `line`: the actual spoken or narrated content, written in **natural, expressive, screenplay-style language**

✅ You **can and should** use names, pronouns, emotions, and inner thoughts freely in `line`.
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
