# 📡 API Reference — Consentinel

> **Base URL**: `http://localhost:8000/api`

All endpoints return JSON. Errors follow the format:

```json
{
  "detail": "Error description"
}
```

---

## 🏥 Health

### `GET /api/health`

Basic liveness check.

**Response** `200 OK`

```json
{
  "status": "healthy",
  "service": "Consentinel",
  "version": "1.0.0"
}
```

### `GET /api/ready`

Readiness check — verifies database connectivity.

**Response** `200 OK`

```json
{
  "status": "ready",
  "database": "connected"
}
```

---

## 👤 Users

### `POST /api/users`

Create a new user profile.

**Request Body**

```json
{
  "external_id": "crm-12345",
  "email": "jane@example.com",
  "name": "Jane Doe",
  "company_name": "Acme Corp",
  "company_size": "mid-market",
  "lifecycle_stage": "trial"
}
```

**Response** `201 Created`

```json
{
  "id": "uuid",
  "external_id": "crm-12345",
  "email": "jane@example.com",
  "name": "Jane Doe",
  "company_name": "Acme Corp",
  "company_size": "mid-market",
  "lifecycle_stage": "trial",
  "intent_score": 0.0,
  "churn_risk": 0.0,
  "activation_score": 0.0,
  "fatigue_score": 0.0,
  "activated": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**curl**

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "name": "Jane Doe"}'
```

### `GET /api/users`

List all users with pagination.

**Query Parameters**

| Param   | Type | Default | Description |
| ------- | ---- | ------- | ----------- |
| `skip`  | int  | 0       | Offset      |
| `limit` | int  | 100     | Max results |

**curl**

```bash
curl http://localhost:8000/api/users?skip=0&limit=10
```

### `GET /api/users/{user_id}`

Get a single user by ID.

**curl**

```bash
curl http://localhost:8000/api/users/{user_id}
```

### `PUT /api/users/{user_id}`

Update user fields.

**Request Body** (all fields optional)

```json
{
  "name": "Jane Smith",
  "lifecycle_stage": "active",
  "company_size": "enterprise"
}
```

**curl**

```bash
curl -X PUT http://localhost:8000/api/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"lifecycle_stage": "active"}'
```

### `DELETE /api/users/{user_id}`

Delete a user profile.

**Response** `200 OK`

```json
{
  "detail": "User deleted"
}
```

### `GET /api/users/{user_id}/scores`

Get computed behavioral scores for a user. Recalculates intent, churn risk, activation, and fatigue scores from event data.

**Response** `200 OK`

```json
{
  "user_id": "uuid",
  "intent_score": 0.72,
  "churn_risk": 0.15,
  "activation_score": 0.5,
  "fatigue_score": 0.3,
  "lifecycle_stage": "active"
}
```

---

## ✅ Consents

### `POST /api/consents`

Record a consent grant for a user on a specific channel.

**Request Body**

```json
{
  "user_id": "uuid",
  "channel": "email",
  "status": "granted",
  "source": "signup_form",
  "region": "EU"
}
```

**curl**

```bash
curl -X POST http://localhost:8000/api/consents \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid", "channel": "email", "status": "granted", "source": "signup_form"}'
```

### `GET /api/consents/{user_id}`

Get all consent records for a user.

**Response** `200 OK`

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "channel": "email",
    "status": "granted",
    "source": "signup_form",
    "region": "EU",
    "granted_at": "2024-01-01T00:00:00Z"
  }
]
```

### `PUT /api/consents/{consent_id}/withdraw`

Withdraw a previously granted consent.

**Response** `200 OK`

```json
{
  "id": "uuid",
  "status": "denied",
  "withdrawn_at": "2024-06-01T00:00:00Z"
}
```

### `POST /api/channel-preferences`

Set channel-specific preferences (frequency caps, quiet hours).

**Request Body**

```json
{
  "user_id": "uuid",
  "channel": "email",
  "frequency_cap_daily": 1,
  "frequency_cap_weekly": 3,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00",
  "topics": ["product_updates", "promotions"]
}
```

### `GET /api/consents/{user_id}/summary`

Get a consent summary across all channels.

**Response** `200 OK`

```json
{
  "user_id": "uuid",
  "channels": {
    "email": { "consented": true, "source": "signup_form" },
    "sms": { "consented": false, "source": null },
    "push": { "consented": true, "source": "app_settings" }
  }
}
```

---

## 📊 Events

### `POST /api/events`

Track a user event.

**Request Body**

```json
{
  "user_id": "uuid",
  "event_type": "track",
  "event_name": "pricing_view",
  "properties": { "plan": "enterprise", "duration_seconds": 45 },
  "source": "web"
}
```

**curl**

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid", "event_type": "track", "event_name": "pricing_view"}'
```

### `GET /api/events/{user_id}`

Get event history for a user.

**Query Parameters**

| Param   | Type | Default | Description |
| ------- | ---- | ------- | ----------- |
| `skip`  | int  | 0       | Offset      |
| `limit` | int  | 100     | Max results |

---

## 🧠 Decisions (Next-Best-Action)

### `POST /api/decisions/next-best-action`

Get the next-best-action decision for a single user. This is the core engine endpoint.

**Request Body**

```json
{
  "user_id": "uuid"
}
```

**Response** `200 OK`

```json
{
  "user_id": "uuid",
  "channel": "email",
  "action": "educate",
  "reason": "High intent detected — sending educational content via consented email channel",
  "suppressed": false,
  "suppression_reason": null,
  "consent_checked": true,
  "fatigue_checked": true,
  "model_confidence": 0.85,
  "created_at": "2024-01-01T00:00:00Z"
}
```

The engine may return `"channel": "none"` and `"action": "none"` when suppression is the best action.

**curl**

```bash
curl -X POST http://localhost:8000/api/decisions/next-best-action \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid"}'
```

### `POST /api/decisions/next-best-action/batch`

Get next-best-action decisions for multiple users at once.

**Request Body**

```json
{
  "user_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

**Response** `200 OK`

```json
{
  "decisions": [
    {"user_id": "uuid-1", "channel": "email", "action": "educate", ...},
    {"user_id": "uuid-2", "channel": "none", "action": "none", ...},
    {"user_id": "uuid-3", "channel": "push", "action": "remind", ...}
  ]
}
```

### `GET /api/decisions/{user_id}`

Get decision history for a user.

### `POST /api/decisions/{decision_id}/explain`

Get an explainability breakdown for a specific decision.

**Response** `200 OK`

```json
{
  "decision_id": "uuid",
  "factors": {
    "intent_score": 0.72,
    "churn_risk": 0.15,
    "fatigue_score": 0.3,
    "consent_status": { "email": true, "sms": false },
    "suppression_rules": [],
    "selected_channel": "email",
    "selected_action": "educate",
    "confidence": 0.85
  },
  "reasoning": "User shows high intent (0.72) with low fatigue (0.30). Email consent is active. Educational content selected to nurture toward conversion."
}
```

---

## 👥 Audiences

### `POST /api/audiences`

Create a new audience segment.

**Request Body**

```json
{
  "name": "High-Intent Trial Users",
  "description": "Trial users with intent score > 0.7",
  "criteria": {
    "lifecycle_stage": "trial",
    "intent_score_min": 0.7
  }
}
```

### `GET /api/audiences`

List all audience segments.

### `GET /api/audiences/{audience_id}`

Get audience details and matching user count.

### `PUT /api/audiences/{audience_id}`

Update an audience segment.

---

## 🗺️ Journeys

### `POST /api/journeys/templates`

Create a journey template (multi-step automated sequence).

**Request Body**

```json
{
  "name": "Onboarding Journey",
  "goal": "activation",
  "steps": [
    {
      "day": 0,
      "channel": "email",
      "action": "educate",
      "content_key": "welcome"
    },
    {
      "day": 2,
      "channel": "push",
      "action": "remind",
      "content_key": "setup_guide"
    },
    {
      "day": 5,
      "channel": "email",
      "action": "offer",
      "content_key": "pro_trial"
    }
  ]
}
```

### `GET /api/journeys/templates`

List all journey templates.

### `POST /api/journeys/{user_id}/enroll`

Enroll a user in a journey.

**Request Body**

```json
{
  "template_id": "uuid"
}
```

### `GET /api/journeys/runs/{user_id}`

Get journey run history for a user.

---

## 🧪 Experiments

### `POST /api/experiments`

Create an A/B experiment.

**Request Body**

```json
{
  "name": "Subject Line Test",
  "hypothesis": "Personalized subject lines increase open rates",
  "variants": [
    { "name": "control", "weight": 50 },
    { "name": "personalized", "weight": 50 }
  ]
}
```

### `GET /api/experiments`

List all experiments.

### `GET /api/experiments/{experiment_id}`

Get experiment details and results.

### `PUT /api/experiments/{experiment_id}/status`

Update experiment status (e.g., start, pause, complete).

**Request Body**

```json
{
  "status": "running"
}
```

---

## 📈 Analytics

### `GET /api/analytics/dashboard`

Get high-level dashboard metrics.

**Response** `200 OK`

```json
{
  "total_users": 1500,
  "total_decisions": 12340,
  "suppression_rate": 0.23,
  "consent_coverage": 0.87,
  "avg_fatigue_score": 0.35,
  "decisions_by_channel": {
    "email": 5200,
    "push": 3100,
    "none": 2840
  },
  "decisions_by_action": {
    "educate": 4500,
    "remind": 2800,
    "none": 2840
  }
}
```

**curl**

```bash
curl http://localhost:8000/api/analytics/dashboard
```

### `GET /api/analytics/cohorts`

Get cohort analysis data.

**Query Parameters**

| Param       | Type   | Description                                 |
| ----------- | ------ | ------------------------------------------- |
| `cohort_by` | string | Field to group by (e.g., `lifecycle_stage`) |
| `metric`    | string | Metric to compute (e.g., `activation_rate`) |

### `GET /api/analytics/funnels`

Get funnel analysis for user journeys.

### `GET /api/analytics/attribution`

Get channel attribution data — which channels drive the most conversions.

### `GET /api/analytics/events-summary`

Get a summary of tracked events grouped by type.

**Response** `200 OK`

```json
{
  "total_events": 45000,
  "by_type": {
    "track": 30000,
    "page": 10000,
    "identify": 5000
  },
  "top_events": [
    { "name": "pricing_view", "count": 4500 },
    { "name": "feature_used", "count": 3200 }
  ]
}
```
