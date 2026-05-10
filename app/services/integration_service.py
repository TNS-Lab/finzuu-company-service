from typing import Any
from urllib.parse import urljoin

import httpx

from app.configs import logger
from app.configs.config import settings
from app.exceptions.AppException import AppException


def public_service_error() -> str:
    return "Unable to complete request"


def client_error_message(service_name: str, description: str) -> str:
    lowered_description = description.lower()

    if service_name == "User service" and "already exist" in lowered_description:
        return "Company admin user already exists"

    if service_name == "User service":
        return "Unable to create company admin user"

    if service_name == "Account service":
        return "Unable to create company operation account"

    return public_service_error()


class IntegrationService:
    async def post(
        self,
        base_url: str,
        path: str,
        payload: dict[str, Any],
        service_name: str,
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        if not base_url:
            logger.error("%s base url is not configured", service_name)
            raise AppException(public_service_error())

        url = urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))
        logger.info("Calling %s: POST %s", service_name, url)
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        if service_name == "Account service" and settings.INTERNAL_SERVICE_TOKEN:
            headers["X-Internal-Service-Name"] = "company-service"
            headers["X-Internal-Service-Token"] = settings.INTERNAL_SERVICE_TOKEN

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_CLIENT_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.exception("Failed to call %s at %s", service_name, url)
            raise AppException(public_service_error()) from exc

        logger.info(
            "%s response: status=%s",
            service_name,
            response.status_code,
        )

        if response.status_code >= 400:
            try:
                response_payload = response.json()
            except ValueError:
                response_payload = {}

            description = response_payload.get("description") or response.text or f"{service_name} request failed"
            logger.error("%s returned %s for %s: %s", service_name, response.status_code, url, description)
            if 400 <= response.status_code < 500:
                raise AppException(
                    client_error_message(service_name, description),
                    status_code=response.status_code,
                )

            raise AppException(public_service_error())

        try:
            return response.json()
        except ValueError:
            return {}
