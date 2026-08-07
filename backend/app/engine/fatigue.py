"""Fatigue scoring engine."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.decision import MessageDecision
from app.models.user import User


class FatigueEngine:
    """Calculates user messaging fatigue based on recent contact history."""

    def calculate_fatigue_score(self, user_id: str, db: Session) -> float:
        """Calculate a fatigue score (0.0–1.0) based on recent messages and responses."""
        recent_count = self.get_recent_contact_count(user_id, db, days=7)

        # Count messages with positive engagement in last 7 days
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        engaged_count = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.user_id == user_id,
                MessageDecision.suppressed.is_(False),
                MessageDecision.created_at >= seven_days_ago,
                MessageDecision.result.in_(["opened", "clicked", "converted"]),
            )
            .count()
        )

        if recent_count == 0:
            return 0.0

        # High volume + low engagement → high fatigue
        engagement_rate = engaged_count / recent_count if recent_count > 0 else 0.0
        volume_factor = min(recent_count / 10.0, 1.0)  # 10+ messages = max volume
        fatigue = volume_factor * (1.0 - engagement_rate)

        return round(min(max(fatigue, 0.0), 1.0), 4)

    def is_fatigued(self, user_id: str, db: Session, threshold: float = 0.80) -> bool:
        """Return True if the user's fatigue score exceeds the threshold."""
        score = self.calculate_fatigue_score(user_id, db)
        return score >= threshold

    def get_recent_contact_count(self, user_id: str, db: Session, days: int = 7) -> int:
        """Count non-suppressed messages sent to the user in the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            db.query(MessageDecision)
            .filter(
                MessageDecision.user_id == user_id,
                MessageDecision.suppressed.is_(False),
                MessageDecision.created_at >= cutoff,
            )
            .count()
        )

    def update_user_fatigue(self, user_id: str, db: Session) -> float:
        """Calculate and persist the fatigue score on the user record."""
        score = self.calculate_fatigue_score(user_id, db)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.fatigue_score = score
            db.commit()
        return score
