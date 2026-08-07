"""Suppression engine — aggregates all suppression checks."""

from sqlalchemy.orm import Session

from app.engine.consent_engine import ConsentEngine
from app.engine.fatigue import FatigueEngine


class SuppressionEngine:
    """Determines whether a message to a user/channel should be suppressed."""

    def __init__(
        self,
        consent_engine: ConsentEngine | None = None,
        fatigue_engine: FatigueEngine | None = None,
    ) -> None:
        self.consent_engine = consent_engine or ConsentEngine()
        self.fatigue_engine = fatigue_engine or FatigueEngine()

    def should_suppress(
        self, user_id: str, channel: str, db: Session
    ) -> tuple[bool, str | None]:
        """Return (suppressed, reason) after running all suppression checks."""
        # 1. Consent check
        if not self.consent_engine.check_channel_consent(user_id, channel, db):
            return True, f"No active consent for {channel}"

        # 2. Fatigue check
        if self.fatigue_engine.is_fatigued(user_id, db):
            return True, "User fatigue threshold exceeded"

        # 3. Frequency cap
        if self.consent_engine.check_frequency_cap(user_id, channel, db):
            return True, f"Daily frequency cap reached for {channel}"

        # 4. Quiet hours
        if self.consent_engine.is_within_quiet_hours(user_id, channel, db):
            return True, f"Within quiet hours for {channel}"

        return False, None

    def get_suppression_reasons(self, user_id: str, db: Session) -> list[dict]:
        """Return all current suppression reasons across channels."""
        channels = ["email", "sms", "push", "in_app", "ad_personalization"]
        reasons: list[dict] = []
        for channel in channels:
            suppressed, reason = self.should_suppress(user_id, channel, db)
            if suppressed:
                reasons.append({"channel": channel, "reason": reason})
        return reasons
