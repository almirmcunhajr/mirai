from typing import Protocol

class Chatbot(Protocol):
    def get_response(self, text: str) -> str:
        ...