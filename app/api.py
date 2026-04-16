from fastapi import APIRouter

from app.routers.company_router import router as company_router
from app.routers.license_router import router as license_router


api_router = APIRouter()

api_router.include_router(company_router, tags=["Company"], prefix="/api/v1/companies")
api_router.include_router(license_router, tags=["License"], prefix="/api/v1/licenses")
