import pytest

from app.exceptions.AppException import AppException
from app.services.integration_service import IntegrationService


class FakeResponse:
    status_code = 400
    text = '{"description":"User with this email already exist"}'

    def json(self):
        return {"description": "User with this email already exist"}


@pytest.mark.asyncio
async def test_integration_service_maps_user_duplicate_to_bad_request(monkeypatch):
    async def fake_post(self, *args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("app.services.integration_service.httpx.AsyncClient.post", fake_post)

    with pytest.raises(AppException) as exc_info:
        await IntegrationService().post(
            base_url="http://user-service.test",
            path="/api/v1/auth/register",
            payload={},
            service_name="User service",
            auth_token="token",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Company admin user already exists"


@pytest.mark.asyncio
async def test_integration_service_adds_internal_headers_for_account_service(monkeypatch):
    captured_headers = {}

    class SuccessResponse:
        status_code = 201

        def json(self):
            return {"status_code": 201}

    async def fake_post(self, *args, **kwargs):
        nonlocal captured_headers
        captured_headers = kwargs["headers"]
        return SuccessResponse()

    monkeypatch.setattr("app.services.integration_service.settings.INTERNAL_SERVICE_TOKEN", "internal-secret")
    monkeypatch.setattr("app.services.integration_service.httpx.AsyncClient.post", fake_post)

    await IntegrationService().post(
        base_url="http://account-service.test",
        path="/api/v1/accounts/",
        payload={},
        service_name="Account service",
        auth_token="user-token",
    )

    assert captured_headers["Authorization"] == "Bearer user-token"
    assert captured_headers["X-Internal-Service-Name"] == "company-service"
    assert captured_headers["X-Internal-Service-Token"] == "internal-secret"
