"""Next-best-action decision endpoints."""

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.consent_engine import ConsentEngine
from app.engine.fatigue import FatigueEngine
from app.engine.next_best_action import NextBestActionEngine
from app.engine.suppression import SuppressionEngine
from app.models.decision import MessageDecision
from app.models.user import User
from app.observability import DECISION_COUNT, DECISION_LATENCY
from app.schemas.decision import (
    DecisionListResponse,
    DecisionRequest,
    DecisionResponse,
    ExplainabilityResponse,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])

consent_engine = ConsentEngine()
fatigue_engine = FatigueEngine()
suppression_engine = SuppressionEngine(consent_engine, fatigue_engine)
nba_engine = NextBestActionEngine(consent_engine, fatigue_engine, suppression_engine)


def _create_decision_record(user_id: str, decision: object) -> MessageDecision:
    return MessageDecision(
        user_id=user_id,
        channel=decision.channel,  # type: ignore[attr-defined]
        action=decision.action,  # type: ignore[attr-defined]
        reason=decision.reason,  # type: ignore[attr-defined]
        consent_checked=decision.consent_checked,  # type: ignore[attr-defined]
        fatigue_checked=decision.fatigue_checked,  # type: ignore[attr-defined]
        suppressed=decision.suppressed,  # type: ignore[attr-defined]
        suppression_reason=decision.suppression_reason,  # type: ignore[attr-defined]
        model_confidence=decision.model_confidence,  # type: ignore[attr-defined]
    )

def _persist_decision(user_id: str, decision: object, db: Session) -> MessageDecision:
    """Save a Decision dataclass to the database."""
    record = _create_decision_record(user_id, decision)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/next-best-action", response_model=DecisionResponse)
def next_best_action(
    payload: DecisionRequest, db: Session = Depends(get_db)
) -> MessageDecision:
    start_time = time.time()
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    decision = nba_engine.decide(user, db)
    record = _persist_decision(user.id, decision, db)

    DECISION_LATENCY.observe(time.time() - start_time)
    DECISION_COUNT.labels(
        suppressed=str(record.suppressed).lower(), channel=record.channel
    ).inc()

    return record


@router.post("/next-best-action/batch", response_model=list[DecisionResponse])
def batch_next_best_action(
    payloads: list[DecisionRequest], db: Session = Depends(get_db)
) -> list[MessageDecision]:
    user_ids = [payload.user_id for payload in payloads]
    users = {user.id: user for user in db.query(User).filter(User.id.in_(user_ids)).all()}
    
    records: list[MessageDecision] = []
    for payload in payloads:
        user = users.get(payload.user_id)
        if not user:
            continue
        decision = nba_engine.decide(user, db)
        records.append(_create_decision_record(user.id, decision))
    
    if records:
        db.add_all(records)
        db.commit()
        for record in records:
            db.refresh(record)
            
    return records


@router.get("/{user_id}", response_model=DecisionListResponse)
def get_decision_history(user_id: str, db: Session = Depends(get_db)) -> dict:
    decisions = (
        db.query(MessageDecision)
        .filter(MessageDecision.user_id == user_id)
        .order_by(MessageDecision.created_at.desc())
        .all()
    )
    return {"decisions": decisions, "total": len(decisions)}


@router.get("/{decision_id}/explain", response_model=ExplainabilityResponse)
def explain_decision(decision_id: str, db: Session = Depends(get_db)) -> dict:
    decision = (
        db.query(MessageDecision).filter(MessageDecision.id == decision_id).first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    user = db.query(User).filter(User.id == decision.user_id).first()
    consent_summary = consent_engine.get_consent_summary(decision.user_id, db)
    suppression_reasons = suppression_engine.get_suppression_reasons(
        decision.user_id, db
    )

    factors: dict = {}
    if user:
        factors = {
            "intent_score": user.intent_score,
            "churn_risk": user.churn_risk,
            "activation_score": user.activation_score,
            "fatigue_score": user.fatigue_score,
            "lifecycle_stage": user.lifecycle_stage,
            "activated": user.activated,
        }

    return {
        "decision_id": decision.id,
        "user_id": decision.user_id,
        "channel": decision.channel,
        "action": decision.action,
        "reason": decision.reason,
        "factors": factors,
        "consent_state": consent_summary,
        "suppression_checks": suppression_reasons,
    }
