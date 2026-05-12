import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware

from .api import api_router
from app.configs import database, logger
from app.configs.config import settings
from app.exceptions.handlers import http_exception_handler
from app.middlewares.log_middleware import log_middleware
from app.services.license_service import LicenseService


async def expire_licenses_once() -> None:
    expired_count = await LicenseService().expire_licenses()
    if expired_count:
        logger.info("Expired %s license(s)", expired_count)


async def expire_licenses_repeated(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await expire_licenses_once()
        except Exception:
            logger.exception("Unable to expire outdated licenses")

        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop_event.wait(), timeout=settings.LICENSE_EXPIRATION_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.initiate_database()
    stop_event = asyncio.Event()
    license_task = asyncio.create_task(expire_licenses_repeated(stop_event))
    
    try:
        yield
    finally:
        stop_event.set()
        license_task.cancel()
        with suppress(asyncio.CancelledError):
            await license_task


app = FastAPI(
    title="Company Service",
    description="Service de gestion des compagnies et de leurs licences",
    version="1.0.1",
    lifespan=lifespan,
    root_path="/company"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Company Service",
        version="1.0.1",
        description="API avec authentification JWT",
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Entrez votre token JWT",
    }
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


logger.info('Starting API ...')
