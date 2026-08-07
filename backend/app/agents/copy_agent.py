"""Copy / message generation agent."""

import json
import os

from openai import OpenAI


class CopyAgent:
    """Generates message copy variants for campaigns."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_copy(
        self,
        context: dict,
        tone: str = "professional",
        objective: str = "educate",
    ) -> dict:
        """Return generated message variants for the given context."""
        if not self.client:
            raise ValueError("OpenAI API key missing or invalid")

        prompt = (
            f"Context: {json.dumps(context)}\n"
            f"Tone: {tone}\n"
            f"Objective: {objective}\n\n"
            "Generate 2 copy variants. Output as JSON with keys 'channel', 'tone', 'objective', 'variants'. "
            "'variants' should be a list of objects with 'variant_id' (A, B), 'subject', 'body', 'cta'."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
