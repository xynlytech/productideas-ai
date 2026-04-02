from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.routers import admin, alerts, auth, clusters, exports, ideas, saved_ideas

settings = get_settings()

# Initialize Sentry
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
        send_default_pii=False,
    )

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="ProductIdeas AI",
    description="Demand intelligence API — discover product opportunities from search signals",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator(
    should_group_status_codes=True,
    excluded_handlers=["/health", "/metrics"],
).instrument(app).expose(app, endpoint="/metrics")

app.include_router(auth.router)
app.include_router(ideas.router)
app.include_router(clusters.router)
app.include_router(saved_ideas.router)
app.include_router(alerts.router)
app.include_router(exports.router)
app.include_router(admin.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
