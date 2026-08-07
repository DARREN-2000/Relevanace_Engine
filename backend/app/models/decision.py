"""Message decision SQLAlchemy model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MessageDecision(Base):
    __tablename__ = "message_decisions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    channel: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(500))

    journey_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("journey_runs.id"), nullable=True
    )
    experiment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("experiments.id"), nullable=True
    )

    consent_checked: Mapped[bool] = mapped_column(Boolean, default=True)
    fatigue_checked: Mapped[bool] = mapped_column(Boolean, default=True)
    suppressed: Mapped[bool] = mapped_column(Boolean, default=False)
    suppression_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    result: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    user = relationship("User", back_populates="decisions")

    def __repr__(self) -> str:
        return f"<MessageDecision {self.channel}:{self.action}>"
