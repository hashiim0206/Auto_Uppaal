# llm_client.py

from groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY


class LLMClient:
    def __init__(self):
        if not GROQ_API_KEY:
            raise RuntimeError("Set GROQ_API_KEY environment variable")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def ask(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature = 0
        )

        msg = response.choices[0].message.content
        return msg.strip()
