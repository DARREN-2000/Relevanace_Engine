"""Journey template and run endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.journey_agent import JourneyAgent
from app.database import get_db
from app.models.journey import JourneyRun, JourneyTemplate
from app.schemas.journey import (
    JourneyDesignRequest,
    JourneyRunResponse,
    JourneyTemplateCreate,
    JourneyTemplateResponse,
)

router = APIRouter(prefix="/journeys", tags=["journeys"])
journey_agent = JourneyAgent()


@router.post("/templates", response_model=JourneyTemplateResponse, status_code=201)
def create_template(
    payload: JourneyTemplateCreate, db: Session = Depends(get_db)
) -> JourneyTemplate:
    template = JourneyTemplate(
        name=payload.name,
        description=payload.description,
        goal=payload.goal,
        audience_id=payload.audience_id,
        steps=payload.steps,
        entry_conditions=payload.entry_conditions,
        exit_conditions=payload.exit_conditions,
        suppression_rules=payload.suppression_rules,
        created_by=payload.created_by,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=list[JourneyTemplateResponse])
def list_templates(db: Session = Depends(get_db)) -> list:
    return db.query(JourneyTemplate).filter(JourneyTemplate.is_active.is_(True)).all()


@router.get("/templates/{template_id}", response_model=JourneyTemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)) -> JourneyTemplate:
    template = (
        db.query(JourneyTemplate).filter(JourneyTemplate.id == template_id).first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Journey template not found")
    return template


@router.post("/design", response_model=JourneyTemplateResponse, status_code=201)
def design_journey(
    payload: JourneyDesignRequest, db: Session = Depends(get_db)
) -> JourneyTemplate:
    audience = payload.audience or {"name": "All users"}
    designed = journey_agent.design_journey(audience, payload.goal)
    template = JourneyTemplate(
        name=designed["name"],
        goal=designed.get("goal"),
        steps=designed["steps"],
        entry_conditions=designed.get("entry_conditions"),
        exit_conditions=designed.get("exit_conditions"),
        suppression_rules=designed.get("suppression_rules"),
        created_by="ai-journey-agent",
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/runs/{user_id}", response_model=list[JourneyRunResponse])
def get_user_journey_runs(user_id: str, db: Session = Depends(get_db)) -> list:
    return (
        db.query(JourneyRun)
        .filter(JourneyRun.user_id == user_id)
        .order_by(JourneyRun.entered_at.desc())
        .all()
    )
