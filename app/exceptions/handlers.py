from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Gestionnaire personnalise pour formater les HTTPException.
    """
    response_types = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }

    response_type = response_types.get(exc.status_code, "ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "response_type": response_type,
            "description": exc.detail,
            "data": None,
        },
    )
