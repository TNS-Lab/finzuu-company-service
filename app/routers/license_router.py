from fastapi import APIRouter, Response, status

from app.models.company_model import Company
from app.models.license_model import License
from app.schemas.license_schema import CreateLicenseSchema
from app.schemas.response_schema import ApiPaginateResponse, ApiResponse
from app.services.company_service import CompanyService
from app.services.license_service import LicenseService
from app.utils.date import has_expired
from app.utils.pagination import get_skip_value, pagination

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiPaginateResponse)
async def get_all(limit: int = 10, page: int = 1):
    skip = get_skip_value(page, limit)
    data = await LicenseService().get_all(skip, limit)
    paginate = await pagination(License, limit, page)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "License data retrieved successfully",
        "data": data,
        "paginate": paginate,
    }


@router.get("/{license_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get(license_id: str, response: Response):
    data = await LicenseService().get_by_id(license_id)

    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "License not found",
            "data": "",
        }

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "License data retrieved successfully",
        "data": data,
    }


@router.get("/company/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get_by_company(company_id: str, response: Response):
    company = await CompanyService().get_by_id(company_id)
    if not company:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    licenses = await LicenseService().get_by_company_id(company_id)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company licenses retrieved successfully",
        "data": {
            "company": company,
            "licenses": licenses,
            "has_active_license": any(license.is_active and not has_expired(license.end_date) for license in licenses),
        },
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def create_license(payload: CreateLicenseSchema, response: Response):
    company = await Company.get(payload.company_id)
    if not company:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    active_license = await LicenseService().get_active_license(payload.company_id)
    if active_license:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "response_type": "Bad Request",
            "description": "An active license already exists for this company",
            "data": "",
        }

    new_license = await LicenseService().create(payload)

    return {
        "status_code": status.HTTP_201_CREATED,
        "response_type": "Success",
        "description": "License created successfully",
        "data": new_license,
    }
