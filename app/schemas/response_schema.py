from typing import Optional, Any
from pydantic import BaseModel


class PaginateResponse(BaseModel):
    total: int
    per_page: int
    current_page: int
    last_page: int

class ApiResponse(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation description",
                "data": "Sample data"
            }
        }

class ApiPaginateResponse(ApiResponse):
    paginate: PaginateResponse

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation description",
                "data": "Sample data",
                "paginate": {
                    "total": 50,
                    "per_page": 15,
                    "current_page": 1,
                    "last_page": 4
                }
            }
        }
