"""Pydantic schemas for Governance endpoints."""

from pydantic import BaseModel


class GovernanceReviewRequest(BaseModel):
    campaign: dict
    consent_state: dict
    fatigue_score: float


class GovernanceReviewResponse(BaseModel):
    decision: str
    issues: list[str]
    warnings: list[str]
    recommendation: str
    requires_human_approval: bool
