from datetime import datetime, timezone
from pydantic import Field, BaseModel

class User(BaseModel):
    """Represents a user in the system."""
    id: str
    email: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 