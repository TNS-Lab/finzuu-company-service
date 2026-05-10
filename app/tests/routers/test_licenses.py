from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import app.auth.permissions as auth_permissions
from app.main import app
from app.models.company_model import Company
from app.models.license_model import CompanySnapshot, License, PackageInfo
from app.tests import database


client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def allow_permissions(monkeypatch):
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 202

        return Response()

    monkeypatch.setattr(auth_permissions.httpx.AsyncClient, "post", fake_post)


def company_payload(**overrides):
    payload = {
        "name": "Licensed Company",
        "short_name": "LICCO",
        "type": "BANK",
        "industries": "Finance",
        "sectors": "Banking",
        "owner": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "owner@example.com",
            "phone": "+237600000000",
            "identity_number": "ID-001",
        },
        "address": {
            "address_line_1": "123 Main Street",
            "street_name": "Main Street",
            "country": "CM",
        },
        "corporation": None,
        "self_sharing": None,
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def license_payload(company):
    return {
        "company_id": company.id,
        "packages": [
            {
                "name": "READY_CASH",
                "description": "Ready Cash package",
            }
        ],
        "duration_days": 30,
        "is_active": True,
    }


async def initiate_database():
    await database.initiate_database()


@pytest.mark.asyncio
async def test_get_all_licenses():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()
    license_document = License(
        start_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 6, 1, tzinfo=timezone.utc),
        company=CompanySnapshot(id=company.id, name=company.name, short_name=company.short_name),
        packages=[PackageInfo(name="READY_CASH", description="Ready Cash package")],
        is_active=True,
    )
    await license_document.insert()

    response = client.get("/api/v1/licenses/", headers=AUTH_HEADERS)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status_code"] == 200
    assert response_json["response_type"] == "Success"
    assert response_json["description"] == "License data retrieved successfully"
    assert response_json["paginate"]["total"] == 1
    assert response_json["data"][0]["id"] == license_document.id
    assert response_json["data"][0]["company"]["id"] == company.id


@pytest.mark.asyncio
async def test_get_license_not_found():
    await initiate_database()

    response = client.get("/api/v1/licenses/unknown_id", headers=AUTH_HEADERS)

    assert response.status_code == 404
    response_json = response.json()
    assert response_json["status_code"] == 404
    assert response_json["response_type"] == "Not Found"
    assert response_json["description"] == "License not found"
    assert response_json["data"] == ""


@pytest.mark.asyncio
async def test_create_license():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()

    response = client.post("/api/v1/licenses/", json=license_payload(company), headers=AUTH_HEADERS)

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["status_code"] == 201
    assert response_json["response_type"] == "Success"
    assert response_json["description"] == "License created successfully"
    assert response_json["data"]["company"]["id"] == company.id
    assert response_json["data"]["packages"][0]["name"] == "READY_CASH"
    assert response_json["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_create_license_company_not_found():
    await initiate_database()

    response = client.post(
        "/api/v1/licenses/",
        json={
            "company_id": "unknown_id",
            "packages": [{"name": "READY_CASH", "description": "Ready Cash package"}],
            "duration_days": 30,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json["status_code"] == 404
    assert response_json["response_type"] == "Not Found"
    assert response_json["description"] == "Company not found"


@pytest.mark.asyncio
async def test_get_licenses_by_company():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()
    license_document = License(
        start_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 6, 1, tzinfo=timezone.utc),
        company=CompanySnapshot(id=company.id, name=company.name, short_name=company.short_name),
        packages=[PackageInfo(name="READY_CASH", description="Ready Cash package")],
        is_active=True,
    )
    await license_document.insert()

    response = client.get(f"/api/v1/licenses/company/{company.id}", headers=AUTH_HEADERS)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status_code"] == 200
    assert response_json["response_type"] == "Success"
    assert response_json["data"]["company"]["id"] == company.id
    assert response_json["data"]["licenses"][0]["id"] == license_document.id
    assert response_json["data"]["has_active_license"] is True


@pytest.mark.asyncio
async def test_update_license():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()
    license_document = License(
        start_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 6, 1, tzinfo=timezone.utc),
        company=CompanySnapshot(id=company.id, name=company.name, short_name=company.short_name),
        packages=[PackageInfo(name="READY_CASH", description="Ready Cash package")],
        is_active=True,
    )
    await license_document.insert()

    response = client.put(
        f"/api/v1/licenses/{license_document.id}",
        json={
            "packages": [{"name": "BULK", "description": "Bulk package"}],
            "is_active": False,
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["description"] == "License updated"
    assert response_json["data"]["packages"][0]["name"] == "BULK"
    assert response_json["data"]["is_active"] is False
