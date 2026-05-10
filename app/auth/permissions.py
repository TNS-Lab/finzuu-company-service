
import httpx
from fastapi import HTTPException, Request, status

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
                detail="Authentication required. Code: 4012",
            )

        if not settings.AUTH_API:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service is not configured",
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
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is unreachable",
            ) from exc

        if response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED):
            return True

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Code: 4013",
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this route or insufficient permissions.",
        )

    return permission_checker
