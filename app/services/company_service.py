import re
from typing import List, Optional

from app.configs import logger
from app.configs.config import settings
from app.exceptions.AppException import AppException
from app.models.company_model import Company
from app.schemas.company_schema import CreateCompanySchema, UpdateCompanySchema
from app.services.integration_service import IntegrationService
from app.utils.key import generate_key


class CompanyService:
    def __init__(self):
        self.integration_service = IntegrationService()

    async def get_all(self, skip: int, limit: int) -> List[Company]:
        return await Company.find_all().skip(skip).limit(limit).to_list()

    async def get_by_id(self, company_id: str) -> Optional[Company]:
        return await Company.get(company_id)

    async def get_by_name_or_short_name(self, name: str, short_name: str) -> Optional[Company]:
        return await Company.find_one(
            {
                "$or": [
                    {"name": name},
                    {"short_name": short_name},
                ]
            }
        )

    async def create(self, payload: CreateCompanySchema, auth_token: str | None = None) -> Company:
        company = Company(
            name=payload.name,
            short_name=payload.short_name,
            type=payload.type,
            industries=payload.industries,
            sectors=payload.sectors,
            owner=payload.owner,
            address=payload.address,
            corporation=payload.corporation,
            self_sharing=payload.self_sharing,
            is_active=payload.is_active,
        )
        await company.insert()

        temp_password = generate_key(12)
        try:
            await self._create_company_admin(company, payload, temp_password, auth_token)
            await self._create_company_operation_account(company, auth_token)
            await self._send_company_creation_notification(company, payload, temp_password, auth_token)
        except Exception:
            await company.delete()
            raise

        return company

    async def set_active(self, company_id: str, is_active: bool) -> Company:
        company = await self.get_by_id(company_id)
        company.is_active = is_active
        await company.save_changes()
        return company

    async def update(self, company_id: str, payload: UpdateCompanySchema) -> Company:
        company = await self.get_by_id(company_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(company, field, value)

        await company.save_changes()
        return company

    async def _create_company_admin(self, company: Company, payload: CreateCompanySchema, temp_password: str, auth_token: str | None = None) -> dict:
        admin_username = self._build_admin_username(payload.admin_first_name, payload.admin_last_name)

        user_payload = {
            "user_name": admin_username,
            "email": payload.admin_email,
            "password": temp_password,
            "type_user": "COMPANY",
            "groupes": ["ADMIN"],
            "identity": company.name,
            "company_id": company.id,
        }
        logger.info(
            "Creating company admin user: company_id=%s email=%s type_user=%s groupes=%s",
            company.id,
            payload.admin_email,
            user_payload["type_user"],
            user_payload["groupes"],
        )

        return await self.integration_service.post(
            base_url=settings.USER_SERVICE_BASE_URL,
            path=settings.USER_SERVICE_CREATE_USER_PATH,
            payload=user_payload,
            service_name="User service",
            auth_token=auth_token,
        )

    async def _create_company_operation_account(self, company: Company, auth_token: str | None = None) -> dict:
        account_payload = {
            "label": f"{company.short_name} OPERATION",
            "currency": "XAF",
            "type": "OPERATION",
            "external_id": company.id,
            "external_class": "COMPANY",
            "owner_identity": {
                "id": company.id,
                "kind": "COMPANY",
                "name": company.name,
                "first_name": company.owner.first_name,
                "last_name": company.owner.last_name,
                "email": company.owner.email,
                "phone": company.owner.phone,
            },
            "direct_momo": False,
            "status": "ACTIVE",
        }
        logger.info(
            "Creating company operation account: company_id=%s external_class=%s type=%s label=%s",
            company.id,
            account_payload["external_class"],
            account_payload["type"],
            account_payload["label"],
        )

        return await self.integration_service.post(
            base_url=settings.ACCOUNT_SERVICE_BASE_URL,
            path=settings.ACCOUNT_SERVICE_CREATE_ACCOUNT_PATH,
            payload=account_payload,
            service_name="Account service",
            auth_token=auth_token,
        )

    async def _send_company_creation_notification(
        self,
        company: Company,
        payload: CreateCompanySchema,
        temp_password: str,
        auth_token: str | None = None,
    ) -> dict:
        if not settings.NOTIFICATION_SERVICE_BASE_URL:
            logger.info("Company creation notification skipped for company %s", company.id)
            return {}

        notification_payload = {
            "to": payload.admin_email,
            "subject": f"Creation de la compagnie {company.name}",
            "template": "company-created",
            "data": {
                "company_id": company.id,
                "company_name": company.name,
                "company_short_name": company.short_name,
                "admin_first_name": payload.admin_first_name,
                "admin_last_name": payload.admin_last_name,
                "temporary_password": temp_password,
            },
        }

        try:
            return await self.integration_service.post(
                base_url=settings.NOTIFICATION_SERVICE_BASE_URL,
                path=settings.NOTIFICATION_SERVICE_SEND_EMAIL_PATH,
                payload=notification_payload,
                service_name="Notification service",
                auth_token=auth_token,
            )
        except AppException as exc:
            logger.warning("Company %s created but notification failed: %s", company.id, exc.message)
            return {}

    @staticmethod
    def _build_admin_username(first_name: str, last_name: str) -> str:
        username = f"{first_name}_{last_name}".strip().lower()
        username = re.sub(r"[^a-z0-9_-]+", "_", username)
        username = re.sub(r"_+", "_", username).strip("_-")
        return username or "company_admin"
