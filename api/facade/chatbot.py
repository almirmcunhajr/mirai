from typing import Protocol, Optional, Any

class Chatbot(Protocol):
    def get_response(self, text: str, options: Optional[Any] = None) -> str:
        """General purpose text completion method."""
        ...