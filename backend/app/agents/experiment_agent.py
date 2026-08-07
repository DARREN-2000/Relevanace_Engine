"""Experiment suggestion agent."""

import json
import os

from openai import OpenAI


class ExperimentAgent:
    """Suggests experiments to improve journey performance."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def suggest_experiment(self, journey_performance: dict) -> dict:
        """Return experiment suggestions based on journey metrics."""
        journey_name = journey_performance.get("journey_name", "Unknown Journey")

        if not self.client:
            raise ValueError("OpenAI API key missing or invalid")

        prompt = (
            f"Journey: {journey_name}\n"
            f"Metrics: {json.dumps(journey_performance)}\n\n"
            "Suggest 1-3 A/B experiments to improve performance. "
            "Output JSON with keys 'journey_name', 'current_metrics', and 'suggestions'. "
            "'suggestions' should be a list of objects with 'experiment_type', 'name', 'description', "
            "'variants' (list of {id, description}), 'traffic_split', 'primary_metric', and 'estimated_duration_days'."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
