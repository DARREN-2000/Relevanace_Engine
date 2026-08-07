"""Journey template and run SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JourneyTemplate(Base):
    __tablename__ = "journey_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    audience_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("audiences.id"), nullable=True
    )
    steps: Mapped[dict] = mapped_column(JSON)
    entry_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    exit_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suppression_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    runs = relationship("JourneyRun", back_populates="template", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<JourneyTemplate {self.name}>"


class JourneyRun(Base):
    __tablename__ = "journey_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    template_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("journey_templates.id"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    exited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    exit_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    template = relationship("JourneyTemplate", back_populates="runs")
    user = relationship("User", back_populates="journey_runs")

    def __repr__(self) -> str:
        return f"<JourneyRun {self.template_id} user={self.user_id}>"
