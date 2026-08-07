import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path to resolve 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, SessionLocal, engine
from app.models.consent import ChannelPreference, Consent
from app.models.event import Event
from app.models.user import User


def seed_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(Event).delete()
        db.query(Consent).delete()
        db.query(ChannelPreference).delete()
        db.query(User).delete()
        db.commit()

        print("Seeding Users...")
        users = [
            User(
                id="user_1",
                external_id="ext_1",
                email="jane@example.com",
                name="Jane Doe",
                lifecycle_stage="trial",
                fatigue_score=0.1,
                intent_score=0.8,
            ),
            User(
                id="user_2",
                external_id="ext_2",
                email="john@example.com",
                name="John Smith",
                lifecycle_stage="paying",
                fatigue_score=0.9,
                intent_score=0.2,
            ),
            User(
                id="user_3",
                external_id="ext_3",
                email="alice@example.com",
                name="Alice Wonderland",
                lifecycle_stage="churned",
                fatigue_score=0.0,
                intent_score=0.1,
            ),
        ]
        db.add_all(users)
        db.commit()

        print("Seeding Consents...")
        consents = [
            Consent(
                user_id="user_1",
                channel="email",
                status="granted",
                source="signup",
                granted_at=datetime.now(timezone.utc),
            ),
            Consent(
                user_id="user_1",
                channel="sms",
                status="granted",
                source="checkout",
                granted_at=datetime.now(timezone.utc),
            ),
            Consent(
                user_id="user_2",
                channel="email",
                status="withdrawn",
                source="preference_center",
                withdrawn_at=datetime.now(timezone.utc),
            ),
        ]
        db.add_all(consents)
        db.commit()

        print("Seeding Events...")
        events = [
            Event(
                user_id="user_1",
                event_type="track",
                event_name="pricing_view",
                properties={"plan": "pro"},
            ),
            Event(
                user_id="user_1",
                event_type="track",
                event_name="checkout_started",
                properties={"value": 100},
            ),
            Event(
                user_id="user_2",
                event_type="track",
                event_name="login",
                properties={"method": "sso"},
            ),
        ]
        db.add_all(events)
        db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
