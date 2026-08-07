"""Consent verification engine."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.consent import ChannelPreference, Consent
from app.models.decision import MessageDecision


class ConsentEngine:
    """Checks and manages user consent state for all channels."""

    def check_channel_consent(self, user_id: str, channel: str, db: Session) -> bool:
        """Return True if user has an active (granted) consent for the channel."""
        consent = (
            db.query(Consent)
            .filter(
                Consent.user_id == user_id,
                Consent.channel == channel,
                Consent.status == "granted",
            )
            .order_by(Consent.created_at.desc())
            .first()
        )
        if consent is None:
            return False
        # Check expiry
        if consent.expires_at and consent.expires_at < datetime.now(timezone.utc):
            return False
        return True

    def get_consented_channels(self, user_id: str, db: Session) -> list[str]:
        """Return list of channels with active consent."""
        consents = (
            db.query(Consent)
            .filter(
                Consent.user_id == user_id,
                Consent.status == "granted",
            )
            .all()
        )
        now = datetime.now(timezone.utc)
        return [c.channel for c in consents if not c.expires_at or c.expires_at >= now]

    def is_within_quiet_hours(
        self,
        user_id: str,
        channel: str,
        db: Session,
        current_time: datetime | None = None,
    ) -> bool:
        """Return True if the current time falls within the user's quiet hours."""
        pref = (
            db.query(ChannelPreference)
            .filter(
                ChannelPreference.user_id == user_id,
                ChannelPreference.channel == channel,
            )
            .first()
        )
        if pref is None or not pref.quiet_hours_start or not pref.quiet_hours_end:
            return False

        now = current_time or datetime.now(timezone.utc)
        current_hm = now.strftime("%H:%M")

        start = pref.quiet_hours_start
        end = pref.quiet_hours_end

        # Handle overnight quiet hours (e.g. 22:00 – 08:00)
        if start <= end:
            return start <= current_hm <= end
        return current_hm >= start or current_hm <= end

    def check_frequency_cap(self, user_id: str, channel: str, db: Session) -> bool:
        """Return True if the daily frequency cap for this channel has been reached."""
        pref = (
            db.query(ChannelPreference)
            .filter(
                ChannelPreference.user_id == user_id,
                ChannelPreference.channel == channel,
            )
            .first()
        )
        if pref is None:
            return False

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        count = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.user_id == user_id,
                MessageDecision.channel == channel,
                MessageDecision.suppressed.is_(False),
                MessageDecision.created_at >= today_start,
            )
            .count()
        )
        return count >= pref.frequency_cap_daily

    def get_consent_summary(self, user_id: str, db: Session) -> dict:
        """Return a summary of consent states for all channels."""
        consents = (
            db.query(Consent)
            .filter(Consent.user_id == user_id)
            .order_by(Consent.created_at.desc())
            .all()
        )
        summary: dict[str, dict] = {}
        now = datetime.now(timezone.utc)
        for c in consents:
            if c.channel not in summary:
                expired = bool(c.expires_at and c.expires_at < now)
                effective_status = (
                    "expired" if expired and c.status == "granted" else c.status
                )
                summary[c.channel] = {
                    "status": effective_status,
                    "source": c.source,
                    "region": c.region,
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                    "withdrawn_at": c.withdrawn_at.isoformat()
                    if c.withdrawn_at
                    else None,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                }
        return summary
