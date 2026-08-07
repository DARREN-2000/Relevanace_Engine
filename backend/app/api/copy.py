"""Copy / message generation endpoints."""

from fastapi import APIRouter

from app.agents.copy_agent import CopyAgent
from app.schemas.copy import CopyGenerateRequest

router = APIRouter(prefix="/copy", tags=["copy"])
copy_agent = CopyAgent()


@router.post("/generate")
def generate_copy(payload: CopyGenerateRequest) -> dict:
    return copy_agent.generate_copy(
        context=payload.context,
        tone=payload.tone,
        objective=payload.objective,
    )
