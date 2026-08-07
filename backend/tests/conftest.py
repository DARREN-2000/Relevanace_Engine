"""Shared test fixtures for the Consentinel test suite."""

import uuid
from datetime import datetime, timezone

import pytest
from app.database import Base, get_db
from app.main import app
from app.models.consent import Consent
from app.models.event import Event
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Yield a clean database session per test."""
    import app.models  # noqa: F401 — register all models

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Yield a TestClient wired to the test database."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── helper data ──────────────────────────────────────────────────────────


@pytest.fixture()
def sample_user(db) -> User:
    """Insert and return a basic user."""
    user = User(
        id=str(uuid.uuid4()),
        email="alice@example.com",
        name="Alice",
        company_name="Acme",
        company_size=10,
        lifecycle_stage="lead",
        intent_score=0.5,
        churn_risk=0.3,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def sample_consent(db, sample_user) -> Consent:
    """Insert a granted email consent for sample_user."""
    consent = Consent(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        channel="email",
        status="granted",
        source="signup_form",
        region="EU",
        granted_at=datetime.now(timezone.utc),
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


@pytest.fixture()
def sample_event(db, sample_user) -> Event:
    """Insert a page_view event for sample_user."""
    event = Event(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        event_type="page_view",
        event_name="pricing_view",
        source="web",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
