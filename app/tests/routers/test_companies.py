import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.exceptions.AppException import AppException
from app.models.company_model import Company
from app.services.company_service import CompanyService
from app.tests import database


client = TestClient(app)


def company_payload(**overrides):
    payload = {
        "name": "Test Company",
        "short_name": "TESTCO",
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
            "address_line_2": None,
            "street_number": "123",
            "street_name": "Main Street",
            "postal_code": "00000",
            "city": "Douala",
            "region": "Littoral",
            "country": "CM",
            "latitude": 4.05,
            "longitude": 9.7,
        },
        "corporation": None,
        "self_sharing": 10,
        "is_active": True,
        "admin_email": "admin@example.com",
        "admin_first_name": "Jane",
        "admin_last_name": "Admin",
    }
    payload.update(overrides)
    return payload


async def noop_integration(*args, **kwargs):
    return {"status_code": 200}


async def initiate_database():
    await database.initiate_database()


@pytest.mark.asyncio
async def test_get_all_companies():
    await initiate_database()

    companies = [
        Company(**company_payload(name="First Company", short_name="FIRST")),
        Company(**company_payload(name="Second Company", short_name="SECOND")),
    ]
    await Company.insert_many(companies)

    response = client.get("/api/v1/companies/")

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status_code"] == 200
    assert response_json["response_type"] == "Success"
    assert response_json["description"] == "Company data retrieved successfully"
    assert response_json["paginate"]["total"] == 2
    assert response_json["data"][0]["id"] == companies[0].id
    assert response_json["data"][0]["name"] == "First Company"
    assert response_json["data"][1]["short_name"] == "SECOND"


@pytest.mark.asyncio
async def test_get_company():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()

    response = client.get(f"/api/v1/companies/{company.id}")

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status_code"] == 200
    assert response_json["response_type"] == "Success"
    assert response_json["data"]["id"] == company.id
    assert response_json["data"]["name"] == company.name
    assert response_json["data"]["owner"]["email"] == "owner@example.com"


@pytest.mark.asyncio
async def test_get_company_not_found():
    await initiate_database()

    response = client.get("/api/v1/companies/unknown_id")

    assert response.status_code == 404
    response_json = response.json()
    assert response_json["status_code"] == 404
    assert response_json["response_type"] == "Not Found"
    assert response_json["description"] == "Company not found"
    assert response_json["data"] == ""


@pytest.mark.asyncio
async def test_create_company(monkeypatch):
    await initiate_database()

    async def fake_create_company_admin(self, company, payload, temp_password):
        return {"status_code": 201}

    async def fake_create_company_operation_account(self, company):
        return {"status_code": 201}

    async def fake_send_company_creation_notification(self, company, payload, temp_password):
        return {"status_code": 200}

    monkeypatch.setattr(CompanyService, "_create_company_admin", fake_create_company_admin)
    monkeypatch.setattr(CompanyService, "_create_company_operation_account", fake_create_company_operation_account)
    monkeypatch.setattr(
        CompanyService,
        "_send_company_creation_notification",
        fake_send_company_creation_notification,
    )

    response = client.post("/api/v1/companies/", json=company_payload())

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["status_code"] == 201
    assert response_json["response_type"] == "Success"
    assert response_json["description"] == "Company created successfully"
    assert response_json["data"]["name"] == "Test Company"
    assert response_json["data"]["short_name"] == "TESTCO"


@pytest.mark.asyncio
async def test_create_company_rolls_back_and_masks_integration_error(monkeypatch):
    await initiate_database()

    async def failing_create_company_admin(self, company, payload, temp_password):
        raise AppException("User service request failed: Authentication required. Code: 4010")

    monkeypatch.setattr(CompanyService, "_create_company_admin", failing_create_company_admin)

    response = client.post("/api/v1/companies/", json=company_payload())

    assert response.status_code == 502
    response_json = response.json()
    assert response_json["description"] == "Unable to complete company creation"
    assert "User service" not in response_json["description"]
    assert await Company.find_one({"name": "Test Company"}) is None


@pytest.mark.asyncio
async def test_create_company_duplicate():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()

    response = client.post("/api/v1/companies/", json=company_payload())

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["status_code"] == 400
    assert response_json["response_type"] == "Bad Request"
    assert response_json["description"] == "A company with this name or short name already exists"


@pytest.mark.asyncio
async def test_update_company():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()

    response = client.put(
        f"/api/v1/companies/{company.id}",
        json={
            "name": "Updated Company",
            "short_name": "UPDATED",
            "type": "IMF",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status_code"] == 200
    assert response_json["response_type"] == "Success"
    assert response_json["description"] == "Company updated"
    assert response_json["data"]["name"] == "Updated Company"
    assert response_json["data"]["short_name"] == "UPDATED"
    assert response_json["data"]["type"] == "IMF"
    assert response_json["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_delete_company():
    await initiate_database()

    company = Company(**company_payload())
    await company.insert()

    response = client.delete(f"/api/v1/companies/{company.id}")

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["description"] == "Company deleted"
    assert await Company.get(company.id) is None


def test_openapi_documents_industries_and_sectors_as_arrays():
    openapi_schema = client.get("/openapi.json").json()
    company_schema = openapi_schema["components"]["schemas"]["CreateCompanySchema"]

    assert company_schema["properties"]["industries"]["type"] == "array"
    assert company_schema["properties"]["sectors"]["type"] == "array"
