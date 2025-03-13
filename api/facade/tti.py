from typing import Protocol, Optional, Any

class TTI(Protocol):
    async def generate_image(self, prompt: str, options: Optional[Any] = None) -> str:
        """Generate an image from a text prompt."""
        ... 