"""Consent management endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.consent_engine import ConsentEngine
from app.models.consent import ChannelPreference, Consent
from app.models.user import User
from app.observability import CONSENT_COVERAGE
from app.schemas.consent import (
    ChannelPreferenceCreate,
    ChannelPreferenceResponse,
    ConsentCreate,
    ConsentResponse,
    ConsentSummary,
)

router = APIRouter(tags=["consents"])


def _update_consent_coverage(db: Session):
    total_users = db.query(User).count()
    if total_users == 0:
        return
    # Count distinct users who have at least one granted consent
    users_with_consent = (
        db.query(Consent.user_id).filter(Consent.status == "granted").distinct().count()
    )
    CONSENT_COVERAGE.set(users_with_consent / total_users)


consent_engine = ConsentEngine()


@router.post("/consents", response_model=ConsentResponse, status_code=201)
def record_consent(payload: ConsentCreate, db: Session = Depends(get_db)) -> Consent:
    granted_at: datetime | None
    if payload.status == "granted":
        granted_at = payload.granted_at or datetime.now(timezone.utc)
    else:
        granted_at = payload.granted_at

    consent = Consent(
        user_id=payload.user_id,
        channel=payload.channel,
        status=payload.status,
        source=payload.source,
        region=payload.region,
        granted_at=granted_at,
        expires_at=payload.expires_at,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)

    _update_consent_coverage(db)
    return consent


@router.get("/consents/{user_id}", response_model=list[ConsentResponse])
def get_user_consents(user_id: str, db: Session = Depends(get_db)) -> list:
    return (
        db.query(Consent)
        .filter(Consent.user_id == user_id)
        .order_by(Consent.created_at.desc())
        .all()
    )


@router.put("/consents/{consent_id}/withdraw", response_model=ConsentResponse)
def withdraw_consent(consent_id: str, db: Session = Depends(get_db)) -> Consent:
    consent = db.query(Consent).filter(Consent.id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    consent.status = "withdrawn"
    consent.withdrawn_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(consent)

    _update_consent_coverage(db)
    return consent


@router.get("/consents/{user_id}/summary", response_model=ConsentSummary)
def consent_summary(user_id: str, db: Session = Depends(get_db)) -> dict:
    summary = consent_engine.get_consent_summary(user_id, db)
    return {"user_id": user_id, "channels": summary}


@router.post(
    "/channel-preferences",
    response_model=ChannelPreferenceResponse,
    status_code=201,
)
def set_channel_preferences(
    payload: ChannelPreferenceCreate, db: Session = Depends(get_db)
) -> ChannelPreference:
    # Upsert: update if exists, create if not
    existing = (
        db.query(ChannelPreference)
        .filter(
            ChannelPreference.user_id == payload.user_id,
            ChannelPreference.channel == payload.channel,
        )
        .first()
    )
    if existing:
        existing.frequency_cap_daily = payload.frequency_cap_daily
        existing.frequency_cap_weekly = payload.frequency_cap_weekly
        existing.quiet_hours_start = payload.quiet_hours_start
        existing.quiet_hours_end = payload.quiet_hours_end
        existing.topics = payload.topics  # type: ignore[assignment]
        db.commit()
        db.refresh(existing)
        return existing

    pref = ChannelPreference(
        user_id=payload.user_id,
        channel=payload.channel,
        frequency_cap_daily=payload.frequency_cap_daily,
        frequency_cap_weekly=payload.frequency_cap_weekly,
        quiet_hours_start=payload.quiet_hours_start,
        quiet_hours_end=payload.quiet_hours_end,
        topics=payload.topics,  # type: ignore[assignment]
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


@router.get(
    "/channel-preferences/{user_id}",
    response_model=list[ChannelPreferenceResponse],
)
def get_channel_preferences(user_id: str, db: Session = Depends(get_db)) -> list:
    return (
        db.query(ChannelPreference).filter(ChannelPreference.user_id == user_id).all()
    )
