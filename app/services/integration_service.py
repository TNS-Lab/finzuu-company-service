from typing import Any
from urllib.parse import urljoin

import httpx

from app.configs import logger
from app.configs.config import settings
from app.exceptions.AppException import AppException


class IntegrationService:
    async def post(self, base_url: str, path: str, payload: dict[str, Any], service_name: str) -> dict[str, Any]:
        if not base_url:
            raise AppException(f"{service_name} base url is not configured")

        url = urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))

        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_CLIENT_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
        except httpx.HTTPError as exc:
            logger.exception("Failed to call %s at %s", service_name, url)
            raise AppException(f"{service_name} is unreachable") from exc

        if response.status_code >= 400:
            try:
                response_payload = response.json()
            except ValueError:
                response_payload = {}

            description = response_payload.get("description") or response.text or f"{service_name} request failed"
            logger.error("%s returned %s for %s: %s", service_name, response.status_code, url, description)
            raise AppException(f"{service_name} request failed: {description}")

        try:
            return response.json()
        except ValueError:
            return {}
