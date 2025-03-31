from typing import Protocol, Type, Any
from enum import StrEnum
from common.base_model_no_extra import BaseModelNoExtra

class ChatOptions(BaseModelNoExtra):
    response_format: Type[BaseModelNoExtra] = None

class ChatMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModelNoExtra):
    role: ChatMessageRole
    content: Any

class Chat(BaseModelNoExtra):
    messages: list[ChatMessage] = []

    def add_user_message(self, message):
        self.messages.append(ChatMessage(role=ChatMessageRole.USER, content=message))

    def add_assistant_response(self, message: str):
        self.messages.append(ChatMessage(role=ChatMessageRole.ASSISTANT, content=message))

    def reset(self):
        self.messages = []

class TTT(Protocol):
    async def chat(self, chat: Chat, options: ChatOptions):
        ...