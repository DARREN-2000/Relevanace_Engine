<p align="center">
  <h1 align="center">🎯 Consentinel</h1>
  <p align="center">
    <strong>The sentinel for consent-first engagement.</strong>
  </p>
  <p align="center">
    "The best marketing action is often no action."
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-api-overview">API</a> •
    <a href="docs/API.md">Full API Docs</a> •
    <a href="docs/DEPLOYMENT.md">Deployment</a>
  </p>
</p>

<!-- Badges -->

![CI](https://github.com/DARREN-2000/Consentinel/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)
![Kubernetes](https://img.shields.io/badge/k8s-helm--ready-326CE5.svg)

---

## 📌 What is Consentinel?

Consentinel is a consent-first next-best-action engine. It puts **user consent at the center** of every decision. Instead of blasting messages to segments, it evaluates each user individually and decides: **should we reach out at all?** If yes — what to say, which channel, and when. If no — it stays silent. Because sometimes the best marketing action is no action.

---

## ✨ Key Features

| Feature                           | Description                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 🧠 **Next-Best-Action Engine**    | AI-driven decision engine that picks the optimal action per user                                       |
| 🛡️ **Consent-First Architecture** | Every action verified against user consent before execution                                            |
| 🤫 **"Do Nothing" as a Feature**  | System can decide to suppress — reducing noise, increasing trust                                       |
| 📊 **Behavioral Scoring**         | Real-time intent, churn risk, activation, and fatigue scoring                                          |
| 🔇 **Fatigue Management**         | Automatic suppression when users are over-contacted                                                    |
| 🗺️ **Journey Orchestration**      | Multi-step automated journeys with consent gates at each step                                          |
| 🧪 **Experimentation**            | Built-in A/B testing framework for continuous optimization                                             |
| 🤖 **AI Agents**                  | Pluggable agents for segmentation, copy, journeys, and governance                                      |
| 📈 **Analytics Dashboard**        | Cohort analysis, funnels, attribution, and decision metrics                                            |
| 🔗 **ConsentHub Integration**     | Companion to [B2B_Consent_Personalization](https://github.com/DARREN-2000/B2B_Consent_Personalization) |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   FastAPI REST API                          │
│  /users  /consents  /events  /decisions  /journeys  /analytics │
└──────┬─────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                  Core Decision Engine                         │
│                                                              │
│  Scoring ──→ Fatigue ──→ Consent ──→ Suppression ──→ NBA    │
│                                                              │
│  "Should we act?"  →  "What action?"  →  "Which channel?"   │
└──────┬───────────────────────────┬───────────────────────────┘
       │                           │
  ┌────▼────┐              ┌───────▼──────┐
  │PostgreSQL│              │    Redis     │
  │ Users    │              │ Cache/Queue  │
  │ Consents │              └──────────────┘
  │ Events   │
  │ Decisions│         ┌──────────────────────┐
  └──────────┘         │    AI Agents Layer    │
                       │ Segment │ Journey     │
                       │ Copy    │ Experiment  │
                       │ Governance            │
                       └──────────────────────┘
```

For the complete architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🔗 Links

- [Product Site (GitHub Pages)](https://darren-2000.github.io/Consentinel/)
- [Live API Demo](https://consentinel.onrender.com/api/health)

---

## 🏆 Competitor Comparison

| Feature              | Consentinel | Braze         | Customer.io   | Iterable      |
| -------------------- | ----------- | ------------- | ------------- | ------------- |
| **Consent-First**    | Native      | Add-on        | Add-on        | Add-on        |
| **Suppression**      | Built-in    | Workaround    | Workaround    | Workaround    |
| **"Do Nothing" NBA** | Core Engine | Custom script | Custom script | Custom script |
| **Self-Hostable**    | Yes         | No            | No            | No            |
| **Open Source**      | Yes         | No            | No            | No            |

---

## 🚀 Quick Start

### Prerequisites

- Docker 24+ & Docker Compose v2+

### Start the Stack

```bash
# Clone
git clone https://github.com/DARREN-2000/Consentinel.git
cd Consentinel

# Configure
cp .env.example .env

# Launch (PostgreSQL + Redis + Backend)
make up

# Verify
curl http://localhost:8000/api/health
```

### Try the API

```bash
# Create a user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "name": "Jane Doe", "lifecycle_stage": "trial"}'

# Record consent
curl -X POST http://localhost:8000/api/consents \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<USER_ID>", "channel": "email", "status": "granted", "source": "signup"}'

# Track an event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<USER_ID>", "event_type": "track", "event_name": "pricing_view"}'

# Get next-best-action decision
curl -X POST http://localhost:8000/api/decisions/next-best-action \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<USER_ID>"}'
```

### Free Demo Deployment (Render)

This repo includes a `render.yaml` so you can deploy a demo in a few clicks on Render's free plan.

1. Fork this repository
2. In Render, choose **New +** → **Blueprint**
3. Select your fork and apply the detected `render.yaml`
4. Wait for deploy, then open:
   - `https://<your-service>.onrender.com/api/health`
   - `https://<your-service>.onrender.com/docs`

> Demo notes: this setup uses SQLite in `/tmp` (ephemeral, non-persistent) and permissive CORS (`["*"]`). For production, use PostgreSQL and restrict CORS to your frontend domain.

---

## 💻 Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run with hot-reload (uses SQLite by default)
uvicorn app.main:app --reload

# Or use Docker with hot-reload
make dev
```

See the full [Development Guide](docs/DEVELOPMENT.md).

---

## 📡 API Overview

| Endpoint                                | Method           | Description                       |
| --------------------------------------- | ---------------- | --------------------------------- |
| `/api/health`                           | GET              | Liveness check                    |
| `/api/ready`                            | GET              | Readiness check (DB connectivity) |
| `/api/users`                            | GET, POST        | List / create users               |
| `/api/users/{id}`                       | GET, PUT, DELETE | User CRUD                         |
| `/api/users/{id}/scores`                | GET              | Behavioral scores                 |
| `/api/consents`                         | POST             | Record consent                    |
| `/api/consents/{user_id}`               | GET              | User consent records              |
| `/api/consents/{user_id}/summary`       | GET              | Consent summary                   |
| `/api/decisions/next-best-action`       | POST             | **Core NBA decision**             |
| `/api/decisions/next-best-action/batch` | POST             | Batch NBA decisions               |
| `/api/decisions/{id}/explain`           | POST             | Decision explainability           |
| `/api/events`                           | POST             | Track events                      |
| `/api/audiences`                        | GET, POST        | Audience segments                 |
| `/api/journeys/templates`               | GET, POST        | Journey templates                 |
| `/api/journeys/{user_id}/enroll`        | POST             | Enroll in journey                 |
| `/api/experiments`                      | GET, POST        | A/B experiments                   |
| `/api/analytics/dashboard`              | GET              | Dashboard metrics                 |
| `/api/analytics/cohorts`                | GET              | Cohort analysis                   |
| `/api/analytics/funnels`                | GET              | Funnel analysis                   |
| `/api/analytics/attribution`            | GET              | Channel attribution               |

Full API documentation: [docs/API.md](docs/API.md)

---

## 📁 Project Structure

```
Consentinel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── api/                 # Route handlers (9 modules)
│   │   ├── engine/              # Core decision logic
│   │   │   ├── next_best_action.py   # NBA engine
│   │   │   ├── consent_engine.py     # Consent verification
│   │   │   ├── fatigue.py            # Fatigue scoring
│   │   │   ├── suppression.py        # Suppression rules
│   │   │   └── scoring.py           # Behavioral scoring
│   │   ├── models/              # SQLAlchemy ORM (8 models)
│   │   ├── schemas/             # Pydantic validation (8 schemas)
│   │   └── agents/              # AI agents (5 agents)
│   ├── tests/                   # pytest suite (10 test modules)
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── helm/                        # Kubernetes Helm chart
│   └── consentinel/
├── docs/                        # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── DEPLOYMENT.md
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml
│   └── cd.yml
├── docker-compose.yml           # Production stack
├── docker-compose.dev.yml       # Dev overrides
├── Makefile                     # Task runner
├── AGENTS.md                    # Copilot agents context
└── .env.example                 # Environment template
```

---

## 💡 Core Innovation: "Do Nothing" is a Valid Action

Most marketing platforms assume every user should receive a message. Consentinel challenges that assumption.

The NBA engine can return `channel: "none"` and `action: "none"` — meaning the best thing to do for this user **right now** is nothing. This happens when:

- **User is fatigued** — too many recent contacts → pause outreach
- **No consent** — no channel has valid consent → stay silent
- **Already activated** — user has completed the goal → stop nudging
- **Quiet hours** — user's preferred quiet period → defer
- **Frequency cap hit** — daily/weekly limits reached → wait

This approach leads to:

- 📉 Lower unsubscribe rates
- 📈 Higher engagement when you do reach out
- 🛡️ Better compliance posture
- 💰 More efficient marketing spend

---

## 🔗 Relationship to ConsentHub

Consentinel is designed as the **action engine** companion to [B2B_Consent_Personalization](https://github.com/DARREN-2000/B2B_Consent_Personalization) (ConsentHub):

|                 | ConsentHub                           | Consentinel                       |
| --------------- | ------------------------------------ | --------------------------------- |
| **Role**        | Consent management & personalization | Decision & action execution       |
| **Decides**     | What consent exists                  | What to do with that consent      |
| **Owns**        | Preference center, consent records   | NBA engine, journeys, experiments |
| **Integration** | Provides consent data via API        | Consumes consent, acts on it      |

Configure the integration:

```env
CONSENTHUB_API_URL=https://consenthub.example.com/api
CONSENTHUB_API_KEY=your-api-key
```

---

## 🧪 Testing

```bash
make test              # Run all tests
make test-cov          # Run with coverage report
make lint              # Lint with ruff
make format            # Auto-format code
```

The test suite covers:

- API endpoint tests (health, users, consents, decisions, events)
- Core engine logic (NBA, consent, fatigue, suppression)
- In-memory SQLite — no external services needed

---

## 🚢 Deployment

### Docker Compose (recommended for single-server)

```bash
make up                # Production stack
make dev               # Development with hot-reload
make logs              # Tail logs
make clean             # Full cleanup
```

### Kubernetes / Helm

```bash
helm install consentinel ./helm/consentinel \
  --namespace consentinel \
  --values values-production.yaml
```

See the full [Deployment Guide](docs/DEPLOYMENT.md).

---

## 📊 KPIs Tracked

| KPI                         | Description                                           |
| --------------------------- | ----------------------------------------------------- |
| **Suppression Rate**        | % of decisions where "do nothing" was the best action |
| **Consent Coverage**        | % of users with at least one active consent           |
| **Decision Confidence**     | Average model confidence across NBA decisions         |
| **Channel Distribution**    | Decision volume per channel                           |
| **Fatigue Score (avg)**     | Average user fatigue across the platform              |
| **Journey Completion Rate** | % of journey runs completed vs. started               |
| **Experiment Lift**         | Measured improvement from A/B experiments             |
| **Engagement Rate**         | Opens + clicks / decisions executed                   |
| **Time-to-Action**          | Latency from event to NBA decision                    |

---

## 🛠️ Tech Stack

| Layer             | Technology                           |
| ----------------- | ------------------------------------ |
| **API Framework** | FastAPI 0.115                        |
| **Language**      | Python 3.12                          |
| **ORM**           | SQLAlchemy 2.0                       |
| **Database**      | PostgreSQL 16                        |
| **Cache**         | Redis 7                              |
| **Validation**    | Pydantic 2.10                        |
| **Auth**          | python-jose (JWT) + passlib          |
| **Migrations**    | Alembic                              |
| **HTTP Client**   | httpx                                |
| **Testing**       | pytest + pytest-cov + pytest-asyncio |
| **Linting**       | Ruff                                 |
| **Containers**    | Docker + Docker Compose              |
| **Orchestration** | Kubernetes + Helm                    |
| **CI/CD**         | GitHub Actions                       |
| **Observability** | Prometheus, OpenTelemetry            |
| **Frontend**      | Vite, React, Recharts                |
| **Agents**        | OpenAI API                           |

---

## 🗺️ Roadmap

| Feature                           | Status         |
| --------------------------------- | -------------- |
| FastAPI Backend                   | ✅ Implemented |
| NBA Engine                        | ✅ Implemented |
| Real DB Seed & Demo Data          | ✅ Implemented |
| OpenTelemetry & Prometheus        | ✅ Implemented |
| LLM-powered Copy & Segment Agents | ✅ Implemented |
| Decision-Evaluation Harness       | ✅ Implemented |
| React/Vite Dashboard              | ✅ Implemented |
| GitHub Pages Site                 | ✅ Implemented |
| LLM-powered Journey Agent         | ✅ Implemented |
| LLM-powered Governance Agent      | ✅ Implemented |

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for marketers who respect their users
</p>
