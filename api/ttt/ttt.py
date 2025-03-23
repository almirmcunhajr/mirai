from typing import Protocol, Any
from pydantic import BaseModel
from enum import StrEnum

class ChatOptions(BaseModel):
    response_format: Any = None

class ChatMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: ChatMessageRole
    content: str

class Chat(BaseModel):
    messages: list[ChatMessage] = []

    def add_user_message(self, message: str):
        self.messages.append(ChatMessage(role=ChatMessageRole.USER, content=message))

    def add_assistant_response(self, message: str):
        self.messages.append(ChatMessage(role=ChatMessageRole.ASSISTANT, content=message))

    def reset(self):
        self.messages = []

class TTT(Protocol):
    async def chat(self, chat: Chat, options: ChatOptions):
        """General purpose chat completion method."""
        ...