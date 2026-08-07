"""Governance / compliance review endpoints."""

from fastapi import APIRouter

from app.agents.governance_agent import GovernanceAgent
from app.schemas.governance import GovernanceReviewRequest, GovernanceReviewResponse

router = APIRouter(prefix="/governance", tags=["governance"])
governance_agent = GovernanceAgent()


@router.post("/review", response_model=GovernanceReviewResponse)
def review_campaign(payload: GovernanceReviewRequest) -> dict:
    return governance_agent.review_campaign(
        campaign=payload.campaign,
        consent_state=payload.consent_state,
        fatigue_score=payload.fatigue_score,
    )
