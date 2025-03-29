from openai import AsyncOpenAI
from enum import Enum

from .ttt import TTT, Chat, ChatOptions

class OpenAIModel(Enum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

class OpenAI(TTT):
    def __init__(self, api_key: str = None, model: OpenAIModel = OpenAIModel.GPT_4O, base_url: str = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def _get_messages(self, chat: Chat) -> list:
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in chat.messages
        ]
    
    async def chat(self, chat: Chat, options: ChatOptions = None):
        if options and options.response_format:
            response = await self.client.responses.create(
                model=self.model.value,
                input=self._get_messages(chat),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": options.response_format.__name__,
                        "schema": options.response_format.model_json_schema()
                    }
                },
                temperature=1.00,
                top_p=1.00,
                store=True
            )
            return options.response_format.model_validate_json(response.output_text)
        response = await self.client.responses.create(
            model=self.model.value,
            input=self._get_messages(chat),
        )
        return response.output_text