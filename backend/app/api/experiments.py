"""Experiment endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.experiment_agent import ExperimentAgent
from app.database import get_db
from app.models.experiment import Experiment
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentSuggestionRequest,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])
experiment_agent = ExperimentAgent()


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    payload: ExperimentCreate, db: Session = Depends(get_db)
) -> Experiment:
    experiment = Experiment(
        name=payload.name,
        description=payload.description,
        experiment_type=payload.experiment_type,
        journey_id=payload.journey_id,
        variants=payload.variants,
        traffic_split=payload.traffic_split,
        status=payload.status,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("", response_model=list[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)) -> list:
    return db.query(Experiment).order_by(Experiment.created_at.desc()).all()


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)) -> Experiment:
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.post("/suggest")
def suggest_experiments(payload: ExperimentSuggestionRequest) -> dict:
    performance = {
        "journey_name": payload.journey_name,
        "open_rate": payload.open_rate,
        "click_rate": payload.click_rate,
        "conversion_rate": payload.conversion_rate,
    }
    return experiment_agent.suggest_experiment(performance)
