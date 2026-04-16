from datetime import datetime, timezone
from typing import List, Optional

from app.configs.config import settings
from app.models.company_model import Company
from app.models.license_model import CompanySnapshot, License, PackageInfo
from app.schemas.license_schema import CreateLicenseSchema
from app.utils.date import add_days, has_expired


class LicenseService:
    async def get_all(self, skip: int, limit: int) -> List[License]:
        return await License.find_all().skip(skip).limit(limit).to_list()

    async def get_by_id(self, license_id: str) -> Optional[License]:
        return await License.get(license_id)

    async def get_by_company_id(self, company_id: str, skip: int = 0, limit: int = 50) -> List[License]:
        return await License.find({"company.id": company_id}).skip(skip).limit(limit).to_list()

    async def get_active_license(self, company_id: str) -> Optional[License]:
        licenses = await License.find(
            {"company.id": company_id, "is_active": True}
        ).sort("-end_date").limit(1).to_list()
        if not licenses:
            return None

        active_license = licenses[0]
        if has_expired(active_license.end_date):
            return None

        return active_license

    async def create(self, payload: CreateLicenseSchema) -> License:
        company = await Company.get(payload.company_id)
        active_license = await self.get_active_license(payload.company_id)

        start_date = payload.start_date or datetime.now(timezone.utc)
        end_date = payload.end_date or add_days(start_date, payload.duration_days or settings.DEFAULT_LICENSE_DURATION_DAYS)

        license_document = License(
            start_date=start_date,
            end_date=end_date,
            company=CompanySnapshot(
                id=company.id,
                name=company.name,
                short_name=company.short_name,
            ),
            packages=[PackageInfo(**package.model_dump()) for package in payload.packages],
            is_active=payload.is_active,
        )

        if active_license:
            active_license.is_active = False
            await active_license.save_changes()

        await license_document.insert()
        return license_document
