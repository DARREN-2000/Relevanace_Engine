"""Tests for NextBestActionEngine.decide_from_state (stateless, no DB)."""

from app.engine.next_best_action import Decision, NextBestActionEngine

engine = NextBestActionEngine()


def test_activated_user_gets_no_action():
    decision = engine.decide_from_state({"activated": True})
    assert decision.channel == "none"
    assert decision.action == "none"
    assert "activated" in decision.reason.lower()


def test_fatigued_user_gets_pause():
    decision = engine.decide_from_state({"fatigue_score": 0.95})
    assert decision.action == "pause"
    assert decision.suppressed is True
    assert decision.suppression_reason == "fatigue"


def test_high_intent_with_email_consent_gets_educate():
    decision = engine.decide_from_state({"intent_score": 0.80, "email_consent": True})
    assert decision.channel == "email"
    assert decision.action == "educate"
    assert decision.model_confidence == 0.85


def test_high_churn_risk_gets_reminder():
    decision = engine.decide_from_state(
        {"churn_risk": 0.75, "email_consent": True, "intent_score": 0.0}
    )
    assert decision.channel == "email"
    assert decision.action == "remind"
    assert decision.model_confidence == 0.8


def test_high_value_company_gets_handoff():
    decision = engine.decide_from_state({"intent_score": 0.90, "company_size": 50})
    assert decision.channel == "crm_task"
    assert decision.action == "handoff"
    assert decision.model_confidence == 0.9


def test_ad_consent_only_gets_retargeting():
    decision = engine.decide_from_state(
        {"ad_personalization_consent": True, "intent_score": 0.0}
    )
    assert decision.channel == "ad_audience"
    assert decision.action == "offer"
    assert decision.model_confidence == 0.6


def test_no_consent_gets_no_action():
    decision = engine.decide_from_state({"intent_score": 0.0})
    assert decision.channel == "none"
    assert decision.action == "none"
    assert "no compliant" in decision.reason.lower()


def test_sms_consent_medium_intent_gets_sms():
    decision = engine.decide_from_state({"intent_score": 0.60, "sms_consent": True})
    assert decision.channel == "sms"
    assert decision.action == "remind"
    assert decision.model_confidence == 0.7


def test_decision_has_correct_fields():
    decision = engine.decide_from_state({"intent_score": 0.80, "email_consent": True})
    assert isinstance(decision, Decision)
    assert isinstance(decision.channel, str)
    assert isinstance(decision.action, str)
    assert isinstance(decision.reason, str)
    assert isinstance(decision.suppressed, bool)
    assert isinstance(decision.consent_checked, bool)
    assert isinstance(decision.fatigue_checked, bool)
