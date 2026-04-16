from typing import List, Optional

from app.models.company_model import Company
from app.schemas.company_schema import CreateCompanySchema, UpdateCompanySchema


class CompanyService:
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

    async def create(self, payload: CreateCompanySchema) -> Company:
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

        # TODO: appeler le service de gestion des utilisateurs pour creer l'utilisateur ADMIN de type COMPANY.
        # TODO: appeler le service de comptes pour creer le compte OPERATION de la compagnie.
        # TODO: appeler le service de notification pour envoyer l'email de creation a l'admin.

        return company

    async def update(self, company_id: str, payload: UpdateCompanySchema) -> Company:
        company = await self.get_by_id(company_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(company, field, value)

        await company.save_changes()
        return company
