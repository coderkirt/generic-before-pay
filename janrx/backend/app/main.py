from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .datastore import DataStore
from .errors import register_error_handlers
from .logging_setup import configure_logging
from .metrics import Metrics
from .middleware import RequestContextMiddleware
from .ocr.service import build_provider
from .ratelimit import SlidingWindowLimiter
from .routers import health, kendras, metrics, ocr, prescription


def create_app(settings: Settings | None = None, ocr_provider=None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="JanRx API", version="0.1.0",
                  docs_url=None if settings.is_prod else "/docs", redoc_url=None,
                  openapi_url=None if settings.is_prod else "/openapi.json")

    app.state.settings = settings
    app.state.metrics = Metrics()
    app.state.limiter = SlidingWindowLimiter(settings.ocr_rate_limit_per_minute, 60)
    app.state.ocr_provider = ocr_provider or build_provider(settings)
    app.state.data = DataStore(settings.data_dir)

    # Order matters: last added is outermost, so request IDs wrap CORS responses too.
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                       allow_methods=["GET", "POST", "OPTIONS"],
                       allow_headers=["Content-Type", "X-Request-ID"],
                       expose_headers=["X-Request-ID", "Retry-After"], max_age=600)
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    for r in (health.router, ocr.router, prescription.router, kendras.router, metrics.router):
        app.include_router(r)
    return app


app = create_app()
