import logging
from typing import Optional, Literal, Type
import re
import time
import random
import copy

from ttt.ttt import TTT, ChatOptions
from script.script import Script, Line, Scene, LineType
from story.story import Subject, Character, Environment, Chat, SubjectType, CharacterGender
from common.genre import Genre
from common.base_model_no_extra import BaseModelNoExtra

class SubjectResponse(BaseModelNoExtra):
    id: int
    type: SubjectType
    name: str
    description: str
    age: Optional[int]
    gender: Optional[CharacterGender]

class SubjectsResponse(BaseModelNoExtra):
    subjects: list[SubjectResponse]

class VisualDescriptionsResponse(BaseModelNoExtra):
    scenes_visual_descriptions: list[str]

class LineResponse(BaseModelNoExtra):
    type: LineType
    character_id: int
    line: str

class LinesResponse(BaseModelNoExtra):
    title: str
    scenes_lines: list[list[LineResponse]]

class ScriptService:
    max_retries=5
    base_delay=1
    max_delay=60

    def __init__(self, ttt: TTT):
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)

    def _get_narrative_generation_message(self, genre: Genre, language: str, decision: str = None) -> str:
        if decision:
            return self._get_decision_message(decision)
        return f''''Generate a compelling {genre.value} narrative in {language}, leading up to a pivotal dilemma for the protagonist.
The story should feature well-developed characters, rich world-building, and emotionally resonant, complex dialogue. Build tension gradually, creating a strong narrative arc that culminates in a meaningful and difficult choice for the protagonist.
        '''
    
    def _get_decision_message(self, decision: str) -> str:
        return f'''I decided to "{decision}".

Reflect deeply on this choice and its potential consequences for the story. Consider how it affects the protagonist, other characters, relationships, motivations, and the world around them.

Then, continue the narrative from this decision point, advancing the story with full narrative momentum. Write with emotional depth, character development, and narrative coherence.

The continuation must lead naturally toward the **next major dilemma** the protagonist must face — or the **conclusion of the story**, if this decision logically propels the plot toward its resolution.

---

### 🧭 Narrative Structure Requirements

- Do **not** end the story early or abruptly  
- The story must follow a clear structure with a **beginning**, **middle**, and **end**  
- Include a strong **climax** and a **well-developed conclusion** if the arc reaches its natural endpoint  
- If the story continues, end the output on a **new pivotal choice** or **dilemma** for the protagonist

---

### ✍️ Writing Style

- Write in natural, immersive prose with narrative and emotional depth  
- Show consequences through actions, interactions, and character growth  
- Maintain consistency in tone, voice, and pacing  
- Avoid summarizing — **narrate events** as they unfold

---

The final output must read as a seamless continuation of the story, shaped by the decision:  
**"{decision}"**
        '''
    
    def _get_subjects_generation_message(self, subjects: dict[str, Subject]) -> str:
        existing_subjects = ''
        if subjects:
            existing_subjects = 'Consider the following existing elements:\n'
            for id in subjects:
                subject = subjects[id]
                if isinstance(subject, Character):
                    existing_subjects += f'type: character\n'
                if isinstance(subject, Environment):
                    existing_subjects += f'type: environment\n'

                existing_subjects += f'id: {id}\n'
                existing_subjects += f'name: {subject.name}\n'
                existing_subjects += f'description: {subject.description}\n'
                if isinstance(subject, Character):
                    existing_subjects += f'age: {subject.age}\n'
                    existing_subjects += f'gender: {subject.gender}\n'
                existing_subjects += '\n'

        return f''''Return the characters and places description of the narrative as fully written descriptive text. The descriptions must be rich, immersive, and naturally integrated, as if written for a novel or screenplay.

Each character and each environment must be assigned a unique **ID number** (integer).

---

### ✅ **Character Description Instructions**

Write descriptive text for each character. The description must reflect the **neutral, consistent visual appearance** of the character — not their current emotional state or momentary expressions.

Include the following elements, woven fluidly into the text:

- Age and gender  
- Skin tone, body type, and posture  
- Facial features: face shape, eyes (color and shape), eyebrows, nose, lips, cheeks, chin, and jawline  
- Hair: texture, length, color, and style  
- Gaze direction (default or typical), without describing mood  
- Neutral hand and gesture tendencies (e.g., left-handed, steady hands)  
- Clothing: typical style, texture, color, and condition  
- Accessories or distinctive physical features (e.g., tattoos, scars, glasses)

❗ Do **not** include emotional traits, mood, or expressions such as smiles, frowns, sadness, or tension — these will vary per scene and must be described in the **scene visual description** instead.

---

### 🏠 **Environment Description Instructions**

Describe each environment in natural, flowing text. Each environment must feel immersive, as if the reader is experiencing it firsthand. Include:

- Whether it is an interior or exterior  
- Type of setting or building  
- Architecture and spatial layout  
- Furniture and notable objects  
- Colors and textures of materials  
- Lighting conditions (source, intensity, color temperature, direction)  
- Time of day and visible weather  
- Ambient details (movement, sound, scent, air)  
- Overall atmosphere in its **default or unoccupied state**

Avoid emotional atmosphere linked to specific characters or events unless they are intrinsic to the place itself.

All elements must be integrated into natural, continuous prose. Do not use list format or attribute labels.

---

Consider the following existing elements:
{existing_subjects}

If no new character or environment is needed, return an empty list. Else, return only the new characters and environments, each with a unique ID number.
        '''
    
    def _get_lines_generation_message(self) -> str:
        return f'''Generate scenes for the narrative.

The output must be a **list of scenes**. Each scene is an object containing:

- A `lines` list: a sequential array of narration and dialogue entries that tell the story within that scene.

---

### 🎬 Scene Structure and Logic

A scene is a **coherent unit of narrative meaning**, defined by a consistent environment, moment, and emotional or action-based beat.

Break the narrative into scenes based on:

- A change in environment or time  
- A shift in action, character interaction, or emotional tone  
- A transition that would require a new cinematic framing or beat

Each scene should reflect a clear transition in story logic — not arbitrary segments of text. Think cinematically.

---

### 🗣️ Line Format (Strict Typing Rules)

Each scene must contain a `lines` field: an ordered list of narrative elements. Each line must be an object with the following structure:

- `type`: `"dialogue"` or `"narration"`  
- `character_id`:  
  - The character’s **ID** (an integer) if `type` is `"dialogue"`  
  - `-1` if `type` is `"narration"`  
- `line`: the spoken or narrated content, written in **natural, expressive, screenplay-style language**

---

### 🔒 STRICT TYPING RULES

**Narration lines (`type: "narration"`):**

- Represent what the **narrator says aloud**, exactly as it should be spoken in voice-over  
- Used only for storytelling transitions, inner monologue (if in narrator's voice), scene descriptions, or emotional commentary  
- Must **not** include any character dialogue or quoted speech  
- Must be fully self-contained and suitable for a TTS narrator to read out loud

**Dialogue lines (`type: "dialogue"`):**

- Represent **direct speech** by characters  
- Must only include what the character **actually says aloud**  
- Must **not** include narration, descriptions, or context — only the character’s spoken words

**NEVER** mix narration and dialogue in the same line. If a line includes both (e.g., action followed by speech), **split it** into separate entries — one `narration` line and one `dialogue` line.

---

### ✅ Writing Guidelines

- Dialogue should reflect each character’s unique voice, emotion, and intent  
- Narration should provide vivid story transitions and emotional flow, suitable for spoken delivery by a narrator  
- All lines must read like a film script: expressive, cinematic, and emotionally grounded  
- Write in the **same language and genre** as the original story  
- Do **not** include visual directions, gestures, camera movements, or sound cues — those will be handled separately

---

The final output must be a **structured list of scenes**, where each scene contains:

- A `lines` array  
- Each `line` object must follow the strict typing and content rules above  
- No extra metadata, formatting, or content outside of this structure
'''
    
    def _get_visual_descriptions_generation_message(self) -> str:
        return f'''**For each scene**, generate a rich, immersive `visual_description`.

The description must convey everything that would be visible in a **single cinematic frame** representing the scene.

This `visual_description` will be used to generate a static image. Therefore, it must capture the **visual composition, character expressions, emotional tone, spatial dynamics, and atmosphere** of the moment.

---

### 🖼️ Visual Description Instructions

Each `visual_description` must include:

- The **environment**, referenced using the format `#<id>` (e.g., `#3`)  
- The **characters present**, referenced using the format `#<id>` (e.g., `#1`, `#2`)  
- The **placement, posture, and interaction** of characters within the space  
- **Facial expressions, gestures, and emotional states** specific to the moment  
- Relevant **props or objects** being used or interacted with  
- **Lighting**, **weather**, and **mood**, if applicable  
- Any ambient or environmental elements that visually define the scene (e.g., smoke, rain, shadows, dust, glowing screens)

---

### 🧾 Format Rules

- Do not include character or environment names — always use their #<id> reference only
- Write in natural, cinematic prose — not a list or structured object  
- Keep the description tightly focused on what is **visually present** in the scene  
- Avoid internal thoughts or narrative exposition — this is a **visual** frame only  
- The text should read like a vivid frame description from a screenplay or storyboard

---

The final output must be a `visual_description` for each scene in the narrative, written as a single descriptive paragraph per scene, referencing all characters and the environment by their `#<id>`.
'''
    def _get_visual_description_improvement_message(self, visual_description: str) -> str:
        return f'''Improve the writing of the following scene visual description. Make sure to not change any characteristic, only improve the writing and make it more concise:
"{visual_description}"
'''
    
    def _parse_lines_response(self, lines_response: LinesResponse, subjects: dict[str, Subject]) -> None:
        all_lines = [line for scene in lines_response.scenes_lines for line in scene]
        errors = []
        for i, line in enumerate(all_lines):
            if line.type == LineType.DIALOGUE:
                if str(line.character_id) not in subjects:
                    msg = f'The character id for the line: "{line.model_dump_json()}" does not exist.'
                    if line.character_id == -1:
                        msg = f'The character id for the line: "{line.model_dump_json()}" is -1. Please, use -1 only for narration lines.'
                    errors.append(msg)
                    continue
                character = subjects[str(line.character_id)]
                if not isinstance(character, Character):
                    errors.append(f'The ID for the line {line.model_dump_json()} does not refer to a character.')
                    continue
        if errors:
            raise ValueError(f'There\'re {len(errors)} issues in your response. Please fix them:\n' + '\n'.join(errors))
    
    def _parse_visual_descriptions_response(self, visual_descriptions_response: VisualDescriptionsResponse, lines_response: LinesResponse, subjects: dict[str, Subject]) -> None:
        if len(visual_descriptions_response.scenes_visual_descriptions) != len(lines_response.scenes_lines):
            raise ValueError(f'You previously generated {len(lines_response)} scenes. The number of visual descriptions does not match the number of scenes. Please generate a visual description for each scene.')

        reference_pattern = re.compile(r"#(\d+)")
        errors = []
        for visual_description in visual_descriptions_response.scenes_visual_descriptions:
            matches = reference_pattern.findall(visual_description)
            for match in matches:
                id = int(match)
                if str(id) not in subjects:
                    errors.append(f'The ID #{id} referenced in the visual description: "{visual_description}" was not found.')
                    continue
        
        if errors:
            raise ValueError(f'There\'re {len(errors)} issues in your response. Please fix them:\n' + '\n'.join(errors))
                
        for i, visual_description in enumerate(visual_descriptions_response.scenes_visual_descriptions):
            substitutions = set()
            for id in subjects:
                subject = subjects[id]
                if id not in substitutions:
                    visual_description = visual_description.replace(f"#{id}", f"{subject.name} ({subject.description})")
                    substitutions.add(id)
                visual_description = visual_description.replace(f"#{id}", f"{subject.name}")
            visual_descriptions_response.scenes_visual_descriptions[i] = visual_description

    def _parse_subjects_response(self, subjects_response: SubjectsResponse, subjects: dict[str, Subject]) -> None:
        errors = []
        for subject_response in subjects_response.subjects:
            if str(subject_response.id) in subjects:
                errors.append(f"The ID {subject_response.id} already exists. Please, do not try to recreate a already existing subject, and always use different IDs for new subjects.")
                continue
            subject = None
            if subject_response.type == SubjectType.CHARACTER:
                subject = Character(
                    name=subject_response.name,
                    description=subject_response.description,
                    age=subject_response.age,
                    gender=subject_response.gender,
                )
            if subject_response.type == SubjectType.ENVIRONMENT:
                subject = Environment(
                    name=subject_response.name,
                    description=subject_response.description,
                )
            subjects[str(subject_response.id)] = subject
        
        if errors:
            raise ValueError(f'There\'re {len(errors)} issues in your response. Please fix them:\n' + '\n'.join(errors))

    async def _exponential_backoff_generate_retry(self, generator: callable, message: str, chat: Chat, response_type: Type[BaseModelNoExtra], parser: callable, *args):
        chat_options = ChatOptions(response_format=response_type)
        chat.add_user_message(message)
        for attempt in range(self.max_retries):
            try:
                response: BaseModelNoExtra = await generator(chat, chat_options)
                chat.add_assistant_response(response.model_dump_json())
                parser(response, *args)
                return response
            except Exception as e:
                chat.add_user_message(str(e))
                wait_time = min(self.base_delay * (2 ** attempt), self.max_delay)
                wait_time = wait_time * random.uniform(0.5, 1.5)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        raise Exception(f"Function failed after {self.max_retries} retries.")

    async def generate(self, chat: Chat, genre: Genre = None, language_code: str = None, decision: str = None, subjects: dict[str, Subject] = {}) -> tuple[Script, dict[str, Subject]]:
        subjects = copy.deepcopy(subjects)

        self.logger.info(f"Generating narrative with genre: {genre}, language: {language_code}, decision: {decision}")
        message = self._get_narrative_generation_message(genre, language_code, decision)
        chat.add_user_message(message)
        chat_options = ChatOptions()
        narrative = await self.ttt.chat(chat, chat_options)
        chat.add_assistant_response(narrative)

        self.logger.info(f"Generating subjects for the narrative")
        message = self._get_subjects_generation_message(subjects)
        await self._exponential_backoff_generate_retry(self.ttt.chat, message, chat, SubjectsResponse, self._parse_subjects_response, subjects)

        self.logger.info(f"Generating lines for the narrative")
        message = self._get_lines_generation_message()
        lines_response: LinesResponse = await self._exponential_backoff_generate_retry(self.ttt.chat, message, chat, LinesResponse, self._parse_lines_response, subjects)

        self.logger.info(f"Generating visual descriptions for the narrative")
        message = self._get_visual_descriptions_generation_message()
        visual_descriptions_response: VisualDescriptionsResponse = await self._exponential_backoff_generate_retry(self.ttt.chat, message, chat, VisualDescriptionsResponse, self._parse_visual_descriptions_response, lines_response, subjects)
        
        scenes = []
        for i, scene_lines in enumerate(lines_response.scenes_lines):
            lines = [Line(**line.model_dump()) for line in scene_lines]
            visual_description = visual_descriptions_response.scenes_visual_descriptions[i]

            self.logger.info(f"Creating a scene with id: {i}, visual description: {visual_description}, lines: {lines}")
            scenes.append(Scene(
                id=i,
                visual_description=visual_description,
                lines=lines
            ))
        
        self.logger.info('Script generated successfully')
        return Script(
            title=lines_response.title,
            genre=genre,
            language=language_code,
            scenes=scenes,
            end=False
        ), subjects