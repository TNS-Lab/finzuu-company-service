from fastapi import APIRouter, Depends, status

from app.auth.permissions import require_permissions
from app.enums import Permission
from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.company_model import Company
from app.models.license_model import License
from app.schemas.license_schema import CreateLicenseSchema, UpdateLicenseSchema
from app.schemas.response_schema import ApiPaginateResponse, ApiResponse
from app.services.company_service import CompanyService
from app.services.license_service import LicenseService
from app.utils.date import has_expired
from app.utils.pagination import get_skip_value, pagination
from app.utils.serialization import serialize_model, serialize_models

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiPaginateResponse)
async def get_all(limit: int = 10, page: int = 1, __=Depends(require_permissions(Permission.LICENSE_READ))):
    skip = get_skip_value(page, limit)
    data = await LicenseService().get_all(skip, limit)
    paginate = await pagination(License, limit, page)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "License data retrieved successfully",
        "data": serialize_models(data),
        "paginate": paginate,
    }


@router.get("/company/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get_by_company(company_id: str, __=Depends(require_permissions(Permission.LICENSE_READ))):
    company = await CompanyService().get_by_id(company_id)
    if not company:
        raise NotFoundException("Company not found")

    licenses = await LicenseService().get_by_company_id(company_id)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company licenses retrieved successfully",
        "data": {
            "company": serialize_model(company),
            "licenses": serialize_models(licenses),
            "has_active_license": any(license.is_active and not has_expired(license.end_date) for license in licenses),
        },
    }


@router.get("/{license_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get(license_id: str, __=Depends(require_permissions(Permission.LICENSE_READ))):
    data = await LicenseService().get_by_id(license_id)

    if not data:
        raise NotFoundException("License not found")

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "License data retrieved successfully",
        "data": serialize_model(data),
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def create_license(payload: CreateLicenseSchema, __=Depends(require_permissions(Permission.LICENSE_CREATE))):
    company = await Company.get(payload.company_id)
    if not company:
        raise NotFoundException("Company not found")

    active_license = await LicenseService().get_active_license(payload.company_id)
    if active_license:
        raise BadRequestException("An active license already exists for this company")

    new_license = await LicenseService().create(payload)

    return {
        "status_code": status.HTTP_201_CREATED,
        "response_type": "Success",
        "description": "License created successfully",
        "data": serialize_model(new_license),
    }


@router.put("/{license_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def update_license(license_id: str, payload: UpdateLicenseSchema, __=Depends(require_permissions(Permission.LICENSE_UPDATE))):
    license_document = await LicenseService().get_by_id(license_id)

    if not license_document:
        raise NotFoundException("License not found")

    updated_license = await LicenseService().update(license_id, payload)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "License updated",
        "data": serialize_model(updated_license),
    }
