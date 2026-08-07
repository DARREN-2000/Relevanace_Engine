"""Core next-best-action decision engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from app.engine.consent_engine import ConsentEngine
from app.engine.fatigue import FatigueEngine
from app.engine.suppression import SuppressionEngine
from app.models.user import User

Channel = Literal["email", "sms", "push", "crm_task", "ad_audience", "in_app", "none"]
Action = Literal["educate", "remind", "offer", "handoff", "pause", "none"]


@dataclass
class Decision:
    """Immutable record of a next-best-action decision."""

    channel: Channel
    action: Action
    reason: str
    suppressed: bool = False
    suppression_reason: str | None = None
    consent_checked: bool = True
    fatigue_checked: bool = True
    model_confidence: float | None = None


class NextBestActionEngine:
    """Consent-first next-best-action decision engine."""

    def __init__(
        self,
        consent_engine: ConsentEngine | None = None,
        fatigue_engine: FatigueEngine | None = None,
        suppression_engine: SuppressionEngine | None = None,
    ) -> None:
        self.consent_engine = consent_engine or ConsentEngine()
        self.fatigue_engine = fatigue_engine or FatigueEngine()
        self.suppression_engine = suppression_engine or SuppressionEngine(
            self.consent_engine, self.fatigue_engine
        )

    def decide(self, user: User, db: Session) -> Decision:
        """Core next-best-action decision logic with full DB access."""
        # 1. Already activated? No action needed
        if user.activated:
            return Decision("none", "none", "User already activated")

        # 2. Check fatigue
        if self.fatigue_engine.is_fatigued(user.id, db):
            return Decision(
                "none",
                "pause",
                "Fatigue cap exceeded",
                suppressed=True,
                suppression_reason="fatigue",
            )

        # 3. Get consented channels
        consented = self.consent_engine.get_consented_channels(user.id, db)

        # 4. Decision tree based on scores and consent

        # High intent, high value — sales handoff
        if user.intent_score > 0.85 and user.company_size and user.company_size > 20:
            return Decision(
                "crm_task",
                "handoff",
                "High-value sales assist",
                model_confidence=0.9,
            )

        # High intent — educational content
        if user.intent_score > 0.75 and "email" in consented:
            suppressed, reason = self.suppression_engine.should_suppress(
                user.id, "email", db
            )
            if suppressed:
                return Decision(
                    "none",
                    "pause",
                    reason or "Suppressed",
                    suppressed=True,
                    suppression_reason=reason,
                )
            return Decision(
                "email",
                "educate",
                "High intent but not activated",
                model_confidence=0.85,
            )

        # High churn risk — retention intervention
        if user.churn_risk > 0.70 and "email" in consented:
            suppressed, reason = self.suppression_engine.should_suppress(
                user.id, "email", db
            )
            if suppressed:
                return Decision(
                    "none",
                    "pause",
                    reason or "Suppressed",
                    suppressed=True,
                    suppression_reason=reason,
                )
            return Decision(
                "email",
                "remind",
                "Retention intervention",
                model_confidence=0.8,
            )

        # Medium intent — push notification
        if user.intent_score > 0.50 and "push" in consented:
            suppressed, reason = self.suppression_engine.should_suppress(
                user.id, "push", db
            )
            if suppressed:
                return Decision(
                    "none",
                    "pause",
                    reason or "Suppressed",
                    suppressed=True,
                    suppression_reason=reason,
                )
            return Decision(
                "push",
                "educate",
                "Medium intent - push engagement",
                model_confidence=0.7,
            )

        # Ad personalization consent — retargeting
        if "ad_personalization" in consented:
            return Decision(
                "ad_audience",
                "offer",
                "Retargeting eligible",
                model_confidence=0.6,
            )

        # In-app available
        if "in_app" in consented:
            return Decision(
                "in_app",
                "educate",
                "In-app guidance",
                model_confidence=0.5,
            )

        # No compliant action
        return Decision("none", "none", "No compliant action available")

    def decide_from_state(self, user_state: dict) -> Decision:
        """Stateless decision from a user state dict (no DB needed)."""
        if user_state.get("activated"):
            return Decision("none", "none", "User already activated")

        if user_state.get("fatigue_score", 0) > 0.80:
            return Decision(
                "none",
                "pause",
                "Fatigue cap exceeded",
                suppressed=True,
                suppression_reason="fatigue",
            )

        email_consent = user_state.get("email_consent", False)
        sms_consent = user_state.get("sms_consent", False)
        ad_consent = user_state.get("ad_personalization_consent", False)
        intent = user_state.get("intent_score", 0)
        churn = user_state.get("churn_risk", 0)
        company_size = user_state.get("company_size", 0)

        if intent > 0.85 and company_size > 20:
            return Decision(
                "crm_task",
                "handoff",
                "High-value sales assist",
                model_confidence=0.9,
            )

        if intent > 0.75 and email_consent:
            return Decision(
                "email",
                "educate",
                "High intent but not activated",
                model_confidence=0.85,
            )

        if churn > 0.70 and email_consent:
            return Decision(
                "email",
                "remind",
                "Retention intervention",
                model_confidence=0.8,
            )

        if intent > 0.50 and sms_consent:
            return Decision(
                "sms",
                "remind",
                "SMS engagement",
                model_confidence=0.7,
            )

        if ad_consent:
            return Decision(
                "ad_audience",
                "offer",
                "Retargeting eligible",
                model_confidence=0.6,
            )

        return Decision("none", "none", "No compliant action available")
