from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from .api import api_router
from app.configs import database, logger
from app.configs.config import settings
from app.middlewares.log_middleware import log_middleware
from app.services.license_service import LicenseService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.initiate_database()
    
    yield


app = FastAPI(
    title="Company Service",
    description="Service de gestion des compagnies et de leurs licences",
    version="1.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

app.include_router(api_router)


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 12, raise_exceptions=False)
async def expire_licenses_task() -> None:
    expired_count = await LicenseService().expire_licenses()

logger.info('Starting API ...')
