import logging

from ttt.ttt import TTT, ChatOptions, Chat
from script.script import Script
from common.genre import Genre
from utils import validate_language


class InvalidLanguageError(Exception):
    """Raised when an invalid language code is provided."""
    pass

class InvalidChatBotResponse(Exception):
    """Raised when the chatbot response is invalid."""
    pass

class ScriptService:
    def __init__(self, ttt: TTT):
        self.ttt = ttt
        self.logger = logging.getLogger(__name__)
        self.chat_options = ChatOptions(response_format=Script)

    def _get_script_generation_initial_message(self, genre: Genre, language: str) -> str:
        return f'''
        Generate a {genre.value} narrative in {language} up to a crucial decision moment. The story should be engaging, with a clear progression of events, culminating in a meaningful choice for the protagonist.

        The narrative should be structured into frames, each representing a moment or scene, with vivid and consistent details about characters and the environment. Each frame should precisely describe visual attributes, emotions, and postures of the characters, as well as lighting, weather, sounds, and objects in the scene, ensuring that characteristics remain uniform throughout the narrative.

        The exhaustive repetition of visual and narrative details must be maintained in all frames to ensure coherence in image generation. Subtle changes, such as alterations in expression, posture, or object positioning, should be explicitly described to ensure logical continuity between frames.

        IMPORTANT: Keep the descriptions family-friendly and avoid any graphic violence, gore, or disturbing content.
        '''
    
    def _get_script_generation_decision_message(self, decision: str) -> str:
        return f'''
        I decided to "{decision}".
        
        Continue the narrative, describe the unfolding events up to the next crucial decision moment or the story's conclusion. The progression of events should be clear, maintaining immersion and ensuring a new significant choice for the protagonist or a impactful conclusion.
        '''

    async def generate(self, chat: Chat = Chat(), genre: Genre = None, language_code: str = None, decision: str = None) -> tuple[Script, Chat]:
        language = validate_language(language_code)
        if not language:
            raise InvalidLanguageError(f"Invalid language code: {language_code}")

        message = self._get_script_generation_initial_message(genre, language)
        if decision:
            message = self._get_script_generation_decision_message(decision)

        chat.add_user_message(message)
        response = await self.ttt.chat(chat, self.chat_options)
        chat.add_assistant_response(response.model_dump_json())
        return response, chat
