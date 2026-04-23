from fastapi import APIRouter, Response, status

from app.exceptions.AppException import AppException
from app.models.company_model import Company
from app.schemas.company_schema import CreateCompanySchema, UpdateCompanySchema
from app.schemas.response_schema import ApiPaginateResponse, ApiResponse
from app.services.company_service import CompanyService
from app.utils.pagination import get_skip_value, pagination

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiPaginateResponse)
async def get_all(limit: int = 10, page: int = 1):
    skip = get_skip_value(page, limit)
    data = await CompanyService().get_all(skip, limit)
    paginate = await pagination(Company, limit, page)

    return {
        "status_code": status.HTTP_200_OK,
        "response_type": "Success",
        "description": "Company data retrieved successfully",
        "data": data,
        "paginate": paginate,
    }


@router.get("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def get(company_id: str, response: Response):
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
        "data": data,
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def create_company(payload: CreateCompanySchema, response: Response):
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
        new_company = await CompanyService().create(payload)
    except AppException as exc:
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return {
            "status_code": status.HTTP_502_BAD_GATEWAY,
            "response_type": "Integration Error",
            "description": exc.message,
            "data": "",
        }

    return {
        "status_code": status.HTTP_201_CREATED,
        "response_type": "Success",
        "description": "Company created successfully",
        "data": new_company,
    }


@router.put("/{company_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def update_company(company_id: str, payload: UpdateCompanySchema, response: Response):
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
        "data": data_updated,
    }
