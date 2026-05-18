from datetime import datetime, timezone
from typing import List, Optional

from app.configs.config import settings
from app.exceptions.custom_exceptions import BadRequestException
from app.models.company_model import Company
from app.models.license_model import CompanySnapshot, License
from app.schemas.license_schema import CreateLicenseSchema, UpdateLicenseSchema
from app.utils.date import add_days, has_expired


class LicenseService:
    def _as_utc(self, value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    def _validate_dates(self, start_date: datetime, end_date: datetime, is_active: bool) -> None:
        start_date = self._as_utc(start_date)
        end_date = self._as_utc(end_date)

        if end_date <= start_date:
            raise BadRequestException("end_date must be greater than start_date")

        if is_active and end_date <= datetime.now(timezone.utc):
            raise BadRequestException("end_date must be in the future for an active license")

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

    async def expire_licenses(self) -> int:
        expired_licenses = await License.find(
            {
                "is_active": True,
                "end_date": {"$lt": datetime.now(timezone.utc)},
            }
        ).to_list()

        for license_document in expired_licenses:
            license_document.is_active = False
            await license_document.save_changes()

        return len(expired_licenses)

    async def create(self, payload: CreateLicenseSchema) -> License:
        company = await Company.get(payload.company_id)
        active_license = await self.get_active_license(payload.company_id)

        start_date = payload.start_date or datetime.now(timezone.utc)
        end_date = payload.end_date or add_days(start_date, payload.duration_days or settings.DEFAULT_LICENSE_DURATION_DAYS)
        self._validate_dates(start_date, end_date, payload.is_active)

        license_document = License(
            start_date=start_date,
            end_date=end_date,
            company=CompanySnapshot(
                id=company.id,
                name=company.name,
                short_name=company.short_name,
            ),
            packages=payload.packages,
            is_active=payload.is_active,
        )

        if active_license:
            active_license.is_active = False
            await active_license.save_changes()

        await license_document.insert()
        return license_document

    async def update(self, license_id: str, payload: UpdateLicenseSchema) -> Optional[License]:
        license_document = await self.get_by_id(license_id)
        if not license_document:
            return None

        update_data = payload.model_dump(exclude_unset=True)

        if "duration_days" in update_data and "start_date" not in update_data and "end_date" not in update_data:
            update_data["end_date"] = add_days(license_document.start_date, update_data["duration_days"])

        update_data.pop("duration_days", None)

        next_start_date = update_data.get("start_date", license_document.start_date)
        next_end_date = update_data.get("end_date", license_document.end_date)
        next_is_active = update_data.get("is_active", license_document.is_active)
        self._validate_dates(next_start_date, next_end_date, next_is_active)

        for field, value in update_data.items():
            setattr(license_document, field, value)

        await license_document.save_changes()
        return license_document
