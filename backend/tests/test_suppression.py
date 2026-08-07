"""Tests for SuppressionEngine."""

from app.engine.suppression import SuppressionEngine

engine = SuppressionEngine()


def test_no_consent_suppressed(db, sample_user):
    """Without any consent records, the channel should be suppressed."""
    suppressed, reason = engine.should_suppress(sample_user.id, "email", db)
    assert suppressed is True
    assert reason is not None
    assert "consent" in reason.lower()


def test_with_consent_not_suppressed(db, sample_user, sample_consent):
    """With a granted consent and no fatigue, should NOT be suppressed."""
    suppressed, reason = engine.should_suppress(sample_user.id, "email", db)
    assert suppressed is False
    assert reason is None
