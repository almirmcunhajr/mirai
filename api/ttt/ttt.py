from typing import Protocol, Optional, Any

class TTT(Protocol):
    async def generate_text(self, text: str, options: Optional[Any] = None) -> str:
        """General purpose text completion method."""
        ...