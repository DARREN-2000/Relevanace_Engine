# AGENTS.md — Consentinel

## Project Overview

Consentinel is a consent-first, AI-powered next-best-action marketing automation platform. It decides whether to send anything at all, then picks the best message, best channel, best time, and best experiment for each user.

## Architecture

- **Backend**: Python/FastAPI REST API
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Cache**: Redis
- **Infrastructure**: Docker Compose, Kubernetes/Helm
- **CI/CD**: GitHub Actions

## Key Concepts

### Core Engine

The NextBestActionEngine evaluates each user's state and decides the optimal action:

1. Check if user is already activated
2. Check fatigue levels
3. Verify consent for each channel
4. Apply suppression rules
5. Select best channel + action based on scores

### "Do Nothing" is Valid

The system can decide to take no action — this is a key differentiator. Suppression of irrelevant marketing is a feature, not a bug.

### Consent-First

Every action passes through consent verification before execution. The system integrates with the companion ConsentHub project (B2B_Consent_Personalization) for consent data.

## Code Structure

- `backend/app/engine/` — Core decision logic
- `backend/app/models/` — SQLAlchemy data models
- `backend/app/api/` — FastAPI route handlers
- `backend/app/schemas/` — Pydantic request/response models
- `backend/app/agents/` — AI agent interfaces (segment, journey, copy, experiment, governance)
- `backend/tests/` — pytest test suite
- `helm/` — Kubernetes Helm chart
- `docs/` — Documentation

## Development

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -v
uvicorn app.main:app --reload
```

## Testing

```bash
make test        # Run tests
make test-cov    # Run tests with coverage
make lint        # Lint with ruff
```
