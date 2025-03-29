from pydantic import BaseModel

class BaseModelNoExtra(BaseModel):
    model_config = {
        "extra": "forbid"
    }