"""Audience management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.segment_agent import SegmentAgent
from app.database import get_db
from app.models.audience import Audience
from app.schemas.audience import (
    AudienceCreate,
    AudienceGenerateRequest,
    AudienceResponse,
)

router = APIRouter(prefix="/audiences", tags=["audiences"])
segment_agent = SegmentAgent()


@router.post("", response_model=AudienceResponse, status_code=201)
def create_audience(payload: AudienceCreate, db: Session = Depends(get_db)) -> Audience:
    audience = Audience(
        name=payload.name,
        description=payload.description,
        definition=payload.definition,
        sql_preview=payload.sql_preview,
        estimated_size=payload.estimated_size,
        created_by=payload.created_by,
    )
    db.add(audience)
    db.commit()
    db.refresh(audience)
    return audience


@router.get("", response_model=list[AudienceResponse])
def list_audiences(db: Session = Depends(get_db)) -> list:
    return db.query(Audience).filter(Audience.is_active.is_(True)).all()


@router.get("/{audience_id}", response_model=AudienceResponse)
def get_audience(audience_id: str, db: Session = Depends(get_db)) -> Audience:
    audience = db.query(Audience).filter(Audience.id == audience_id).first()
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    return audience


@router.post("/generate", response_model=AudienceResponse, status_code=201)
def generate_audience(
    payload: AudienceGenerateRequest, db: Session = Depends(get_db)
) -> Audience:
    generated = segment_agent.generate_audience(payload.goal, payload.event_schema)
    audience = Audience(
        name=generated["name"],
        description=generated.get("description"),
        definition=generated["definition"],
        estimated_size=generated.get("estimated_size"),
        created_by="ai-segment-agent",
    )
    db.add(audience)
    db.commit()
    db.refresh(audience)
    return audience
