import json

from fastapi import Request, status
from starlette.types import ASGIApp

from app.auth import permissions as auth_permissions
from app.configs import logger


class AuthMiddleware:
    """
    ASGI middleware that validates authentication and route access globally.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path

        if request.method == "OPTIONS" or path in auth_permissions.PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        auth_header = auth_permissions.get_auth_header(request)
        if not auth_header:
            await self.send_json_response(
                send,
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "response_type": "Unauthorized",
                    "description": "Authentication required",
                    "data": None,
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            return

        if not auth_permissions.settings.AUTH_API:
            logger.error("Authentication service is not configured")
            await self.send_json_response(
                send,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "response_type": "Internal Server Error",
                    "description": "Unable to process authentication",
                    "data": None,
                },
            )
            return

        try:
            async with auth_permissions.httpx.AsyncClient(
                timeout=auth_permissions.settings.HTTP_CLIENT_TIMEOUT_SECONDS
            ) as client:
                response = await client.post(
                    f"{auth_permissions.settings.AUTH_API.rstrip('/')}/api/v1/auth/check-permission",
                    json={"route": path, "permission": []},
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": auth_header,
                    },
                )
        except auth_permissions.httpx.HTTPError as exc:
            logger.exception("Authentication service is unreachable")
            await self.send_json_response(
                send,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
                    "response_type": "ERROR",
                    "description": "Unable to process authentication",
                    "data": None,
                },
            )
            return

        if response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED):
            await self.app(scope, receive, send)
            return

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            await self.send_json_response(
                send,
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "response_type": "Unauthorized",
                    "description": "Authentication required",
                    "data": None,
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            return

        await self.send_json_response(
            send,
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status_code": status.HTTP_403_FORBIDDEN,
                "response_type": "Forbidden",
                "description": "You do not have access to this route",
                "data": None,
            },
        )

    async def send_json_response(self, send, status_code: int, content: dict, headers: dict | None = None):
        response_headers = [(b"content-type", b"application/json")]

        if headers:
            for key, value in headers.items():
                response_headers.append((key.lower().encode(), value.encode()))

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": response_headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(content).encode(),
            }
        )
