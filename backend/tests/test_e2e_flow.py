import uuid

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_e2e_flow():
    # 1. Create a user
    user_payload = {
        "email": "e2e_user_" + str(uuid.uuid4()) + "@example.com",
        "name": "E2E User",
        "lifecycle_stage": "trial",
    }
    response = client.post("/api/users", json=user_payload)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # 2. Record consent
    consent_payload = {
        "user_id": user_id,
        "channel": "email",
        "status": "granted",
        "source": "signup",
    }
    response = client.post("/api/consents", json=consent_payload)
    assert response.status_code == 201

    # 3. Track event
    event_payload = {
        "user_id": user_id,
        "event_type": "track",
        "event_name": "pricing_view",
    }
    response = client.post("/api/events", json=event_payload)
    assert response.status_code == 201

    # 4. Next-best-action decision
    decision_payload = {"user_id": user_id}
    response = client.post("/api/decisions/next-best-action", json=decision_payload)
    assert response.status_code == 200
    decision_id = response.json()["id"]
    action = response.json()["action"]
    assert action is not None

    # 5. Explain decision
    response = client.get(f"/api/decisions/{decision_id}/explain")
    assert response.status_code == 200
    explain = response.json()
    assert explain["decision_id"] == decision_id
    assert explain["user_id"] == user_id
    assert "factors" in explain
    assert "consent_state" in explain
    assert "suppression_checks" in explain
