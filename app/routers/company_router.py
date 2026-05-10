from fastapi import APIRouter, Depends, Request, Response, status

from app.auth.permissions import require_permissions
from app.configs import logger
from app.enums import Permission
from app.exceptions.AppException import AppException
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
async def get_all(limit: int = 10, page: int = 1, __=Depends(require_permissions(Permission.COMPANY_COMPANY_READ))):
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
async def get(company_id: str, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_READ))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company data retrieved successfully",
        "data": serialize_model(data),
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def create_company(payload: CreateCompanySchema, request: Request, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_CREATE))):
    existing_company = await CompanyService().get_by_name_or_short_name(payload.name, payload.short_name)
    if existing_company:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "response_type": "Bad Request",
            "description": "A company with this name or short name already exists",
            "data": "",
        }

    try:
        new_company = await CompanyService().create(payload, auth_token=get_bearer_token(request))
    except AppException as exc:
        logger.error("Company creation failed during inter-service orchestration: %s", exc.message)
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return {
            "status_code": status.HTTP_502_BAD_GATEWAY,
            "response_type": "Integration Error",
            "description": "Unable to complete company creation",
            "data": "",
        }

    return {
        "status_code": status.HTTP_201_CREATED,
        "response_type": "Success",
        "description": "Company created successfully",
        "data": serialize_model(new_company),
    }


@router.put("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def update_company(company_id: str, payload: UpdateCompanySchema, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_UPDATE))):
    data_to_update = await CompanyService().get_by_id(company_id)

    if not data_to_update:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Resource not found",
            "description": "An error occurred. Company not found",
            "data": "",
        }

    data_updated = await CompanyService().update(company_id, payload)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company updated",
        "data": serialize_model(data_updated),
    }


@router.patch("/{company_id}/activate", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def activate_company(company_id: str, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_ACTIVATE))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    data_updated = await CompanyService().set_active(company_id, True)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company activated",
        "data": serialize_model(data_updated),
    }


@router.patch("/{company_id}/deactivate", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def deactivate_company(company_id: str, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_DEACTIVATE))):
    data = await CompanyService().get_by_id(company_id)

    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    data_updated = await CompanyService().set_active(company_id, False)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company deactivated",
        "data": serialize_model(data_updated),
    }


@router.delete("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def delete_company(company_id: str, response: Response, __=Depends(require_permissions(Permission.COMPANY_COMPANY_UPDATE))):
    deleted = await CompanyService().delete(company_id)

    if not deleted:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_type": "Not Found",
            "description": "Company not found",
            "data": "",
        }

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company deleted",
        "data": "",
    }
