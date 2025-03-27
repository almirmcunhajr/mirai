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
            completion = await self.client.beta.chat.completions.parse(
                model=self.model.value,
                messages=self._get_messages(chat),
                response_format=options.response_format,
            )
            return completion.choices[0].message.parsed
        completion = await self.client.chat.completions.create(
            model=self.model.value,
            messages=self._get_messages(chat),
        )
        return completion.choices[0].message.content