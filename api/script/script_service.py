import logging

from ttt.ttt import TTT, ChatOptions, Chat
from script.script import Script, Scene
from story.story import Character
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
    scenes: list[Scene]
    end: bool

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
        return f'''Generate a {genre.value} narrative in {language} up to a impactful decision moment. 
The story should be engaging, with a strong development of the characters and narrative, and complex dialogs, culminating in a choice for the protagonist.
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
- `scenes`: array of scene objects, each containing:
  - `id`: string (e.g., `"1"`, `"2"`)
  - `visual_description`: string — see strict rules below
  - `lines`: array of objects with:
    - `type`: `"dialogue"` or `"narration"`
    - `character`: name of the speaker (use `"Narrator"` only for general narration)
    - `line`: the actual spoken or narrated content
- `end`: boolean indicating if the story has reached its conclusion

Make sure to preserve the original language of the narrative in the narrations and dialogues.

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

Every character must be described with the following:

#### ✅ **Full Physical Description** (Use this level of granularity **every time**):

- **Age range** (e.g., early 40s)  
- **Gender**  
- **Skin tone** (e.g., light brown, pale, ebony)  
- **Body type and posture** (e.g., athletic build with broad shoulders; slim frame with a hunched stance)  
- **Face**:  
  - **Shape** (e.g., angular, oval, round)  
  - **Eye color and shape** (e.g., almond-shaped hazel eyes)  
  - **Eyebrows** (e.g., thick and arched, or sparse and flat)  
  - **Nose** (e.g., straight and narrow, wide and rounded)  
  - **Mouth and lips** (e.g., full lips slightly parted, thin lips pressed tight)  
  - **Cheeks** (e.g., sunken, rosy, freckled)  
  - **Chin and jawline** (e.g., strong jaw with a cleft chin)  
  - **Visible micro-expressions** (e.g., subtle smirk, trembling lower lip, twitching eyelid)  
- **Hair**: texture, color, length, and style (e.g., shoulder-length curly auburn hair tied in a loose bun)  
- **Eyes and gaze direction** (e.g., eyes narrowed, looking downward; wide-eyed stare into the distance)  
- **Hands and gestures** (e.g., fingers twitching, hands clenched into fists, one hand adjusting a sleeve)  
- **Clothing**:  
  - **Type, style, texture, and color** (e.g., loose beige linen shirt tucked into worn-out jeans)  
  - **Condition** (e.g., pristine, wrinkled, stained, torn)  
- **Accessories or distinctive features**:  
  - (e.g., wireframe glasses, scar on left eyebrow, tribal tattoo on right forearm, silver wedding ring)

> ⚠️ These details must be unique and **re-stated** in full for each scene, **even if the same character reappears**.

---

### 🏠 LOCATION DESCRIPTION TEMPLATE

Every location must be fully described as if the viewer has never seen it before:

- Interior or exterior  
- Type of building or setting (e.g., rustic cabin, neon-lit alley, cathedral nave)  
- Architecture and layout  
- Furniture and notable objects  
- Colors and textures of materials (e.g., cracked plaster walls, dusty wooden floors)  
- Lighting conditions (natural or artificial, warm or cold light, harsh shadows or soft glows)  
- Time of day and visible weather  
- Ambient elements (e.g., flickering candle, buzzing neon, rustling leaves)  
- Atmosphere and mood (e.g., tense silence, cozy warmth, sterile emptiness)

> 💡 Each `visual_description` must stand alone — it should be enough to generate a full image without relying on any previous scenes.

---

### 🎭 `lines` rules:

Each scene must include an array called `lines`, in **sequential order**, containing both dialogue and narration.

Each line must be an object with:
- `type`: `"dialogue"` or `"narration"`
- `character`: speaker's name  
  - Use `"Narrator"` only for general exposition or scene-setting narration
- `line`: the actual spoken or narrated content, written in **natural, expressive, screenplay-style language**

Make sure the dialogue is **natural and engaging**, with a focus on character development. 

⚠️ Do not rush the dialogue or narration. It should feel **natural and unhurried**, allowing the reader to fully immerse in the story.

✅ You **can and should** use names, pronouns, emotions, and inner thoughts freely in `line`.
        '''
    def _get_characteres_message(self) -> str:
        return f'''Based on the story or script, extract the list of characters and return them as a JSON object.

The value for each character must be an object containing:
    - name: the character's name
    - age: approximate age (as an integer)
    - gender: "male", "female"

⚠️ The character names used as keys must **exactly match** the names used in the "character" fields inside the lines array of the script (both for dialogue and narration). This ensures voice-matching works properly later.

Only include characters who speak or narrate in the script.
Do not include "Narrator" — it is a system voice, not a character.
'''
    
    def _get_invalid_characters_message(self, not_found: list[str]) -> str:
        return f''''The following characters were not found in the characters response: {', '.join(not_found)}.
Please ensure that the character names in the script match the names in the characters response.
'''
    
    def _get_decision_message(self, decision: str) -> str:
        return f'''I decided to "{decision}".
Reflect deeply on this choice and its potential consequences for the story. Then, generate the continuation of the narrative up to the next impactful decision moment, or the end of the story if appropriate.

Make sure to respect the rules established in the previous messages:

### 📸 `visual_description` rules (STRICT AND NON-NEGOTIABLE):

This field must be a **single, complete, and self-contained string**, describing the scene **as if no prior context exists**.

#### ❌ NEVER USE:
- Pronouns (e.g., “he”, “she”, “they”, “his”, “her”)
- Character names (e.g., “Lucas”, “Maria”)
- Vague references (e.g., “the young woman”, “the couple”, “the house”, “the same violin player”)

#### ✅ ALWAYS:
- Fully re-describe **every character**, **every location**, and **every object**, **from scratch**, in **every scene**, even if they have appeared before.

---

Every character must be described with the following:

#### ✅ **Full Physical Description** (Use this level of granularity **every time**):

- **Age range** (e.g., early 40s)  
- **Gender**  
- **Skin tone** (e.g., light brown, pale, ebony)  
- **Body type and posture** (e.g., athletic build with broad shoulders; slim frame with a hunched stance)  
- **Face**:  
  - **Shape** (e.g., angular, oval, round)  
  - **Eye color and shape** (e.g., almond-shaped hazel eyes)  
  - **Eyebrows** (e.g., thick and arched, or sparse and flat)  
  - **Nose** (e.g., straight and narrow, wide and rounded)  
  - **Mouth and lips** (e.g., full lips slightly parted, thin lips pressed tight)  
  - **Cheeks** (e.g., sunken, rosy, freckled)  
  - **Chin and jawline** (e.g., strong jaw with a cleft chin)  
  - **Visible micro-expressions** (e.g., subtle smirk, trembling lower lip, twitching eyelid)  
- **Hair**: texture, color, length, and style (e.g., shoulder-length curly auburn hair tied in a loose bun)  
- **Eyes and gaze direction** (e.g., eyes narrowed, looking downward; wide-eyed stare into the distance)  
- **Hands and gestures** (e.g., fingers twitching, hands clenched into fists, one hand adjusting a sleeve)  
- **Clothing**:  
  - **Type, style, texture, and color** (e.g., loose beige linen shirt tucked into worn-out jeans)  
  - **Condition** (e.g., pristine, wrinkled, stained, torn)  
- **Accessories or distinctive features**:  
  - (e.g., wireframe glasses, scar on left eyebrow, tribal tattoo on right forearm, silver wedding ring)

> ⚠️ These details must be unique and **re-stated** in full for each scene, **even if the same character reappears**.

---

### 🏠 LOCATION DESCRIPTION TEMPLATE

Every location must be fully described as if the viewer has never seen it before:

- Interior or exterior  
- Type of building or setting (e.g., rustic cabin, neon-lit alley, cathedral nave)  
- Architecture and layout  
- Furniture and notable objects  
- Colors and textures of materials (e.g., cracked plaster walls, dusty wooden floors)  
- Lighting conditions (natural or artificial, warm or cold light, harsh shadows or soft glows)  
- Time of day and visible weather  
- Ambient elements (e.g., flickering candle, buzzing neon, rustling leaves)  
- Atmosphere and mood (e.g., tense silence, cozy warmth, sterile emptiness)

> 💡 Each `visual_description` must stand alone — it should be enough to generate a full image without relying on any previous scenes.

Do not end the story early. The narrative must have a clear beginning, middle, and end, with proper climax and well developed conclusion.
'''
    
    def _get_not_found_characters(self, characters_response: CharactersResponse, script_response: ScriptResponse) -> list[str]:
        lines_characters = set([line.character for scene in script_response.scenes for line in scene.lines if line.type == "dialogue"])
        characters_names = set([character.name for character in characters_response.characters])
        not_found_characters = []
        for character in lines_characters:
            if character not in characters_names:
                self.logger.error(f"Character '{character}' not found in characters response.")
                not_found_characters.append(character)
        if not_found_characters:
            return not_found_characters
        return []
    
    async def _get_characters(self, chat: Chat, script_response: ScriptResponse):
        not_found = []
        while True:
            message = self._get_characteres_message()
            if not_found:
                message = self._get_invalid_characters_message(not_found)
            chat.add_user_message(message)
            
            chat_options = ChatOptions(response_format=CharactersResponse)
            characters_response: CharactersResponse = await self.ttt.chat(chat, chat_options)
            chat.add_assistant_response(characters_response.model_dump_json())

            not_found = self._get_not_found_characters(characters_response, script_response)
            if not not_found:
                return [Character(name=character.name, age=character.age, gender=character.gender) for character in characters_response.characters]
    
    async def generate(self, chat: Chat, genre: Genre = None, language_code: str = None, decision: str = None) -> tuple[Script, list[Character]]:
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

        characters = await self._get_characters(chat, script_response)
        return Script(
            title=script_response.title,
            genre=genre,
            language=language_code,
            scenes=script_response.scenes,
            end=script_response.end
        ), characters
