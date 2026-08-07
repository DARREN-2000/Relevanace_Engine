"""Journey design agent."""

import json
import os

from openai import OpenAI


class JourneyAgent:
    """Designs multi-step journeys from audience definitions and goals."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def design_journey(self, audience: dict, goal: str) -> dict:
        """Return a journey with steps tailored to the goal."""
        if not self.client:
            raise ValueError("OpenAI API key missing or invalid")

        prompt = (
            f"Audience: {json.dumps(audience)}\n"
            f"Goal: {goal}\n\n"
            "Design a multi-step journey for this audience and goal. "
            "Output JSON with keys 'name', 'goal', 'audience', 'steps' (list of objects with 'step', 'type', 'action', 'delay_hours', 'subject'), "
            "'entry_conditions', 'exit_conditions', and 'suppression_rules'."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
