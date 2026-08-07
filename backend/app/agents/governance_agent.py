"""Governance / compliance review agent."""

import json
import os

from openai import OpenAI


class GovernanceAgent:
    """Reviews campaigns for compliance with consent and fatigue rules."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def review_campaign(
        self,
        campaign: dict,
        consent_state: dict,
        fatigue_score: float,
    ) -> dict:
        """Return an approve / suppress / reject decision with reasons."""
        if not self.client:
            raise ValueError("OpenAI API key missing or invalid")

        prompt = (
            f"Campaign: {json.dumps(campaign)}\n"
            f"Consent State: {json.dumps(consent_state)}\n"
            f"Fatigue Score: {fatigue_score}\n\n"
            "Review this campaign against compliance and brand safety rules. "
            "Output JSON with keys 'status' (approved, suppressed, or rejected), "
            "'issues' (list of strings), and 'warnings' (list of strings)."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
