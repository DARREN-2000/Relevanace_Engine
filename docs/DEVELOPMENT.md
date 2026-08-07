# 🛠️ Development Guide — Consentinel

## Prerequisites

| Tool           | Version | Purpose             |
| -------------- | ------- | ------------------- |
| Python         | 3.12+   | Backend runtime     |
| Docker         | 24+     | Containerization    |
| Docker Compose | v2+     | Local orchestration |
| Make           | any     | Task runner         |
| Git            | 2.40+   | Version control     |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/DARREN-2000/Consentinel.git
cd Consentinel
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 3. Option A: Docker Compose (recommended)

```bash
# Start full stack (PostgreSQL + Redis + Backend)
make up

# Or for development with hot-reload
make dev
```

The API will be available at `http://localhost:8000`.

### 3. Option B: Local Python environment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Run with SQLite (no external database needed)
uvicorn app.main:app --reload --port 8000
```

By default the backend uses SQLite for development. Set `DATABASE_URL` to a PostgreSQL connection string for production mode.

---

## Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
cd backend && python -m pytest tests/test_next_best_action.py -v

# Run with verbose output
cd backend && python -m pytest tests/ -v --tb=long
```

Tests use an in-memory SQLite database by default — no external services needed.

---

## Code Style

We use **Ruff** for linting and formatting.

```bash
# Lint
make lint

# Auto-format
make format
```

### Rules

- Follow PEP 8 naming conventions
- Use type hints for all function parameters and return values
- Docstrings for public functions (Google style)
- Max line length: 88 characters (Black-compatible)

---

## Project Structure

```
Consentinel/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   │
│   │   ├── api/                 # Route handlers
│   │   │   ├── health.py        # GET /health, /ready
│   │   │   ├── users.py         # User CRUD
│   │   │   ├── consents.py      # Consent management
│   │   │   ├── decisions.py     # Next-best-action decisions
│   │   │   ├── events.py        # Event tracking
│   │   │   ├── audiences.py     # Audience segmentation
│   │   │   ├── journeys.py      # Journey templates & runs
│   │   │   ├── experiments.py   # A/B experiments
│   │   │   └── analytics.py     # Dashboard & reporting
│   │   │
│   │   ├── engine/              # Core decision logic
│   │   │   ├── next_best_action.py  # NBA engine
│   │   │   ├── consent_engine.py    # Consent verification
│   │   │   ├── fatigue.py           # Fatigue scoring
│   │   │   ├── suppression.py       # Suppression rules
│   │   │   └── scoring.py          # User behavior scoring
│   │   │
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── consent.py
│   │   │   ├── event.py
│   │   │   ├── decision.py
│   │   │   ├── audience.py
│   │   │   ├── journey.py
│   │   │   ├── experiment.py
│   │   │   └── audit.py
│   │   │
│   │   ├── schemas/             # Pydantic request/response models
│   │   │   ├── user.py
│   │   │   ├── consent.py
│   │   │   ├── decision.py
│   │   │   ├── event.py
│   │   │   ├── audience.py
│   │   │   ├── journey.py
│   │   │   ├── experiment.py
│   │   │   └── analytics.py
│   │   │
│   │   └── agents/              # AI agent interfaces
│   │       ├── segment_agent.py
│   │       ├── journey_agent.py
│   │       ├── copy_agent.py
│   │       ├── experiment_agent.py
│   │       └── governance_agent.py
│   │
│   ├── tests/                   # Test suite
│   │   ├── conftest.py          # Fixtures
│   │   ├── test_health.py
│   │   ├── test_api_users.py
│   │   ├── test_api_consents.py
│   │   ├── test_api_decisions.py
│   │   ├── test_api_events.py
│   │   ├── test_consent_engine.py
│   │   ├── test_fatigue.py
│   │   ├── test_next_best_action.py
│   │   └── test_suppression.py
│   │
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── helm/                        # Kubernetes Helm chart
├── docs/                        # Documentation
├── docker-compose.yml           # Production stack
├── docker-compose.dev.yml       # Dev overrides
├── Makefile                     # Task runner
└── .env.example                 # Environment template
```

---

## Adding New Endpoints

### 1. Create the model (if needed)

```python
# backend/app/models/my_resource.py
from sqlalchemy import Column, String
from app.database import Base
import uuid


class MyResource(Base):
    __tablename__ = "my_resources"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
```

### 2. Create the schema

```python
# backend/app/schemas/my_resource.py
from pydantic import BaseModel


class MyResourceCreate(BaseModel):
    name: str


class MyResourceResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True
```

### 3. Create the router

```python
# backend/app/api/my_resource.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.my_resource import MyResource
from app.schemas.my_resource import MyResourceCreate, MyResourceResponse

router = APIRouter(prefix="/my-resources", tags=["my-resources"])


@router.post("/", response_model=MyResourceResponse, status_code=201)
def create(data: MyResourceCreate, db: Session = Depends(get_db)):
    resource = MyResource(name=data.name)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource
```

### 4. Register the router

```python
# backend/app/main.py — add to the router includes
from app.api import my_resource

app.include_router(my_resource.router, prefix=settings.API_PREFIX)
```

### 5. Write tests

```python
# backend/tests/test_my_resource.py
def test_create_resource(client):
    response = client.post("/api/my-resources/", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

### 6. Create a migration

```bash
cd backend
alembic revision --autogenerate -m "add my_resources table"
alembic upgrade head
```

---

## Useful Commands

| Command          | Description                       |
| ---------------- | --------------------------------- |
| `make help`      | Show all available make targets   |
| `make up`        | Start production stack            |
| `make dev`       | Start dev stack with hot-reload   |
| `make test`      | Run tests                         |
| `make test-cov`  | Run tests with coverage           |
| `make lint`      | Lint code                         |
| `make format`    | Auto-format code                  |
| `make logs`      | Tail backend logs                 |
| `make db-shell`  | Open PostgreSQL shell             |
| `make redis-cli` | Open Redis CLI                    |
| `make clean`     | Remove all containers and volumes |
