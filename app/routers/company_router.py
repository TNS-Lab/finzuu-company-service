from fastapi import APIRouter, Depends, Request, status

from app.auth.permissions import require_permissions
from app.configs import logger
from app.enums import Permission
from app.exceptions.custom_exceptions import BadRequestException, IntegrationException, NotFoundException
from app.models.company_model import Company
from app.schemas.company_schema import CreateCompanySchema, UpdateCompanySchema
from app.schemas.response_schema import ApiPaginateResponse, ApiResponse
from app.services.company_service import CompanyService
from app.utils.pagination import get_skip_value, pagination
from app.utils.serialization import serialize_model, serialize_models

router = APIRouter()


def get_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]

    return request.cookies.get("access_token")


@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiPaginateResponse)
async def get_all(limit: int = 10, page: int = 1, __=Depends(require_permissions(Permission.COMPANY_READ))):
    skip = get_skip_value(page, limit)
    data = await CompanyService().get_all(skip, limit)
    paginate = await pagination(Company, limit, page)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company data retrieved successfully",
        "data": serialize_models(data),
        "paginate": paginate,
    }


@router.get("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get(company_id: str, __=Depends(require_permissions(Permission.COMPANY_READ))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        raise NotFoundException("Company not found")

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company data retrieved successfully",
        "data": serialize_model(data),
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def create_company(payload: CreateCompanySchema, request: Request, __=Depends(require_permissions(Permission.COMPANY_CREATE))):
    existing_company = await CompanyService().get_by_name_or_short_name(payload.name, payload.short_name)
    if existing_company:
        raise BadRequestException("A company with this name or short name already exists")

    try:
        new_company = await CompanyService().create(payload, auth_token=get_bearer_token(request))
    except IntegrationException as exc:
        logger.error("Company creation failed during inter-service orchestration: %s", exc.detail)
        raise IntegrationException(
            "Unable to complete company creation",
            status_code=exc.status_code,
        ) from exc

    return {
        "status_code": status.HTTP_201_CREATED,
        "response_type": "Success",
        "description": "Company created successfully",
        "data": serialize_model(new_company),
    }


@router.put("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def update_company(company_id: str, payload: UpdateCompanySchema, __=Depends(require_permissions(Permission.COMPANY_UPDATE))):
    data_to_update = await CompanyService().get_by_id(company_id)

    if not data_to_update:
        raise NotFoundException("Company not found")

    data_updated = await CompanyService().update(company_id, payload)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company updated",
        "data": serialize_model(data_updated),
    }


@router.patch("/{company_id}/activate", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def activate_company(company_id: str, __=Depends(require_permissions(Permission.COMPANY_UPDATE))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        raise NotFoundException("Company not found")

    data_updated = await CompanyService().set_active(company_id, True)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company activated",
        "data": serialize_model(data_updated),
    }


@router.patch("/{company_id}/deactivate", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def deactivate_company(company_id: str, __=Depends(require_permissions(Permission.COMPANY_UPDATE))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        raise NotFoundException("Company not found")

    data_updated = await CompanyService().set_active(company_id, False)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company deactivated",
        "data": serialize_model(data_updated),
    }
