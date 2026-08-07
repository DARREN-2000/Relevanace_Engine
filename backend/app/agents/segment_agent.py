"""Segment / audience generation agent."""

import json
import os

from openai import OpenAI


class SegmentAgent:
    """Generates audience definitions from natural-language goals."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_audience(self, goal: str, event_schema: dict | None = None) -> dict:
        """Return generated audience definition with inclusion/exclusion rules."""
        if not self.client:
            raise ValueError("OpenAI API key missing or invalid")

        prompt = (
            f"Goal: {goal}\n"
            f"Event Schema: {json.dumps(event_schema) if event_schema else 'None'}\n\n"
            "Generate an audience definition. Output JSON with keys 'name', 'description', 'definition' (which has 'include' and 'exclude' lists), and 'estimated_size'."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
