"""Consentinel — FastAPI application factory."""

import logging
logger = logging.getLogger(__name__)

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from prometheus_client import make_asgi_app

from app.api import (
    analytics,
    audiences,
    consents,
    copy,
    decisions,
    events,
    experiments,
    governance,
    health,
    journeys,
    users,
)
from app.config import settings
from app.database import Base, engine

# Setup OpenTelemetry tracer
trace.set_tracer_provider(TracerProvider())


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create database tables on startup."""
    import app.models  # noqa: F401 — ensure models are registered

    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description=(
            "Consent-first, AI-powered next-best-action marketing automation platform"
        ),
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Metrics
    metrics_app = make_asgi_app()
    application.mount("/metrics", metrics_app)

    # Instrument FastAPI for tracing
    FastAPIInstrumentor.instrument_app(application)

    # Routers
    prefix = settings.API_PREFIX
    application.include_router(health.router, prefix=prefix)
    application.include_router(users.router, prefix=prefix)
    application.include_router(consents.router, prefix=prefix)
    application.include_router(events.router, prefix=prefix)
    application.include_router(decisions.router, prefix=prefix)
    application.include_router(audiences.router, prefix=prefix)
    application.include_router(journeys.router, prefix=prefix)
    application.include_router(experiments.router, prefix=prefix)
    application.include_router(copy.router, prefix=prefix)
    application.include_router(governance.router, prefix=prefix)
    application.include_router(analytics.router, prefix=prefix)

    # Global exception handler
    @application.exception_handler(Exception)
    async def global_exception_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception:")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    return application


app = create_app()
