"""User SQLAlchemy model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    lifecycle_stage: Mapped[str] = mapped_column(String(50), default="unknown")
    intent_score: Mapped[float] = mapped_column(Float, default=0.0)
    churn_risk: Mapped[float] = mapped_column(Float, default=0.0)
    activation_score: Mapped[float] = mapped_column(Float, default=0.0)
    fatigue_score: Mapped[float] = mapped_column(Float, default=0.0)
    preferred_channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_meaningful_touchpoint: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activated: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    consents = relationship("Consent", back_populates="user", lazy="selectin")
    channel_preferences = relationship(
        "ChannelPreference", back_populates="user", lazy="selectin"
    )
    events = relationship("Event", back_populates="user", lazy="dynamic")
    decisions = relationship("MessageDecision", back_populates="user", lazy="dynamic")
    journey_runs = relationship("JourneyRun", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.email or self.external_id or self.id}>"
