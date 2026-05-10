
import httpx
from fastapi import HTTPException, Request, status

from app.configs import logger
from app.configs.config import settings


PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/company/health",
    "/company/docs",
    "/company/openapi.json",
    "/company/redoc",
}


def get_auth_header(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header

    access_token = request.cookies.get("access_token")
    if access_token:
        return f"Bearer {access_token}"

    return None


def require_permissions(*permissions: str):
    async def permission_checker(request: Request):
        if request.url.path in PUBLIC_PATHS:
            return True

        auth_header = get_auth_header(request)
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not settings.AUTH_API:
            logger.error("Authentication service is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to process authentication",
            )

        payload = {
            "route": request.url.path,
            "permission": list(permissions),
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_CLIENT_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{settings.AUTH_API.rstrip('/')}/api/v1/auth/check-permission",
                    json=payload,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            logger.exception("Authentication service is unreachable")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to process authentication",
            ) from exc

        if response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED):
            return True

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            logger.warning("Authentication rejected by auth service with status %s", response.status_code)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.warning("Permission denied by auth service with status %s", response.status_code)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return permission_checker
