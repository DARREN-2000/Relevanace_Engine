"""User scoring engine for intent, churn risk, and activation."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.user import User

# Events that signal high purchase intent
_HIGH_INTENT_EVENTS = {
    "pricing_view",
    "demo_request",
    "plan_comparison",
    "checkout_start",
}
_ACTIVATION_EVENTS = {
    "signup",
    "onboarding_complete",
    "first_integration",
    "invite_team",
}


class ScoringEngine:
    """Calculates behavioural scores for users."""

    def calculate_intent_score(self, user_id: str, db: Session) -> float:
        """Score 0.0–1.0 based on recent high-intent events."""
        fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
        events = (
            db.query(Event)
            .filter(
                Event.user_id == user_id,
                Event.timestamp >= fourteen_days_ago,
            )
            .all()
        )

        if not events:
            return 0.0

        total = len(events)
        high_intent = sum(1 for e in events if e.event_name in _HIGH_INTENT_EVENTS)
        page_views = sum(1 for e in events if e.event_type == "page_view")

        # Weighted combination
        intent_ratio = high_intent / max(total, 1)
        activity_factor = min(total / 20.0, 1.0)  # 20+ events = max
        pv_factor = min(page_views / 10.0, 0.3)  # page views contribute up to 0.3

        score = (intent_ratio * 0.6) + (activity_factor * 0.1) + pv_factor
        return round(min(max(score, 0.0), 1.0), 4)

    def calculate_churn_risk(self, user_id: str, db: Session) -> float:
        """Score 0.0–1.0 based on declining activity."""
        now = datetime.now(timezone.utc)

        recent_count = (
            db.query(Event)
            .filter(
                Event.user_id == user_id,
                Event.timestamp >= now - timedelta(days=7),
            )
            .count()
        )
        previous_count = (
            db.query(Event)
            .filter(
                Event.user_id == user_id,
                Event.timestamp >= now - timedelta(days=14),
                Event.timestamp < now - timedelta(days=7),
            )
            .count()
        )

        if previous_count == 0 and recent_count == 0:
            return 0.5  # Unknown risk

        if previous_count == 0:
            return 0.0  # New user with some activity

        drop_off = 1.0 - (recent_count / previous_count)
        return round(min(max(drop_off, 0.0), 1.0), 4)

    def calculate_activation_score(self, user_id: str, db: Session) -> float:
        """Score 0.0–1.0 based on completion of activation milestones."""
        events = db.query(Event).filter(Event.user_id == user_id).all()

        completed = {e.event_name for e in events if e.event_name in _ACTIVATION_EVENTS}
        if not completed:
            return 0.0

        return round(len(completed) / len(_ACTIVATION_EVENTS), 4)

    def update_user_scores(self, user_id: str, db: Session) -> dict:
        """Calculate all scores and persist them on the user record."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        intent = self.calculate_intent_score(user_id, db)
        churn = self.calculate_churn_risk(user_id, db)
        activation = self.calculate_activation_score(user_id, db)

        user.intent_score = intent
        user.churn_risk = churn
        user.activation_score = activation
        db.commit()
        db.refresh(user)

        return {
            "intent_score": intent,
            "churn_risk": churn,
            "activation_score": activation,
        }
