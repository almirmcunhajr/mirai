from openai import OpenAI

class ChatGPT:
    def __init__(self, api_key: str, model = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def get_response(self, text: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}]
        )
        return completion.choices[0].message.content