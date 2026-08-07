"""Analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.decision import MessageDecision
from app.models.event import Event
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsSummary,
    ChannelMetrics,
    FatigueDistribution,
    SuppressionStats,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)) -> dict:
    total_users = db.query(User).count()
    total_decisions = db.query(MessageDecision).count()
    total_events = db.query(Event).count()

    suppressed_count = (
        db.query(MessageDecision).filter(MessageDecision.suppressed.is_(True)).count()
    )
    suppression_rate = (
        suppressed_count / total_decisions if total_decisions > 0 else 0.0
    )

    avg_intent = db.query(func.avg(User.intent_score)).scalar() or 0.0
    avg_churn = db.query(func.avg(User.churn_risk)).scalar() or 0.0
    avg_fatigue = db.query(func.avg(User.fatigue_score)).scalar() or 0.0

    activated_users = db.query(User).filter(User.activated.is_(True)).count()
    activation_rate = activated_users / total_users if total_users > 0 else 0.0

    return {
        "total_users": total_users,
        "total_decisions": total_decisions,
        "total_events": total_events,
        "suppression_rate": round(suppression_rate, 4),
        "avg_intent_score": round(float(avg_intent), 4),
        "avg_churn_risk": round(float(avg_churn), 4),
        "avg_fatigue_score": round(float(avg_fatigue), 4),
        "activated_users": activated_users,
        "activation_rate": round(activation_rate, 4),
    }


@router.get("/channels", response_model=list[ChannelMetrics])
def channel_performance(db: Session = Depends(get_db)) -> list[dict]:
    channels = ["email", "sms", "push", "crm_task", "ad_audience", "in_app"]
    metrics: list[dict] = []

    for channel in channels:
        total = (
            db.query(MessageDecision).filter(MessageDecision.channel == channel).count()
        )
        if total == 0:
            continue

        suppressed = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.channel == channel,
                MessageDecision.suppressed.is_(True),
            )
            .count()
        )
        delivered = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.channel == channel,
                MessageDecision.result == "delivered",
            )
            .count()
        )
        opened = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.channel == channel,
                MessageDecision.result == "opened",
            )
            .count()
        )
        clicked = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.channel == channel,
                MessageDecision.result == "clicked",
            )
            .count()
        )
        converted = (
            db.query(MessageDecision)
            .filter(
                MessageDecision.channel == channel,
                MessageDecision.result == "converted",
            )
            .count()
        )

        non_suppressed = total - suppressed
        metrics.append(
            {
                "channel": channel,
                "total_decisions": total,
                "suppressed": suppressed,
                "delivered": delivered,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "suppression_rate": round(suppressed / total, 4) if total else 0.0,
                "open_rate": round(opened / non_suppressed, 4)
                if non_suppressed
                else 0.0,
                "click_rate": round(clicked / non_suppressed, 4)
                if non_suppressed
                else 0.0,
            }
        )

    return metrics


@router.get("/fatigue", response_model=list[FatigueDistribution])
def fatigue_distribution(db: Session = Depends(get_db)) -> list[dict]:
    total = db.query(User).count() or 1
    buckets = [
        ("0.0-0.2", 0.0, 0.2),
        ("0.2-0.4", 0.2, 0.4),
        ("0.4-0.6", 0.4, 0.6),
        ("0.6-0.8", 0.6, 0.8),
        ("0.8-1.0", 0.8, 1.01),
    ]
    result: list[dict] = []
    for label, low, high in buckets:
        count = (
            db.query(User)
            .filter(User.fatigue_score >= low, User.fatigue_score < high)
            .count()
        )
        result.append(
            {
                "bucket": label,
                "count": count,
                "percentage": round(count / total, 4),
            }
        )
    return result


@router.get("/suppression", response_model=list[SuppressionStats])
def suppression_stats(db: Session = Depends(get_db)) -> list[dict]:
    suppressed = (
        db.query(MessageDecision).filter(MessageDecision.suppressed.is_(True)).all()
    )
    total = len(suppressed) or 1
    reasons: dict[str, int] = {}
    for d in suppressed:
        reason = d.suppression_reason or "unknown"
        reasons[reason] = reasons.get(reason, 0) + 1

    return [
        {
            "reason": reason,
            "count": count,
            "percentage": round(count / total, 4),
        }
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1])
    ]
