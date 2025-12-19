from openai import OpenAI
from core.services.config.config_manager import ConfigManager
import json


class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.config = ConfigManager()

    def request_openai(
        self,
        prompt: str | dict,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
    ) -> str:
        """
        Send a request to OpenAI.
        - If `prompt` is a str → passed as user-only message (system role is empty).
        - If `prompt` is a dict → expects {"system": "...", "user": "..."}.
        """
        if isinstance(prompt, str):
            # simple text prompt → only user role
            input_messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, dict):
            system_msg = prompt.get("system", "")
            user_msg = prompt.get("user", "")
            input_messages = []
            if system_msg:
                input_messages.append({"role": "system", "content": system_msg})
            if user_msg:
                input_messages.append({"role": "user", "content": user_msg})
        else:
            raise TypeError("prompt must be str or dict with 'system' and 'user'")

        result = self.client.responses.create(
            model=model,
            input=json.dumps(input_messages),
            temperature=temperature,
        )

        return result.output_text