from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.enums import PackageName


class PackageSchema(BaseModel):
    name: PackageName = Field(..., description="Package activé par la licence.")
    description: str = Field(..., description="Description lisible du package.", examples=["Accès aux fonctionnalités Ready Cash"])


class CreateLicenseSchema(BaseModel):
    company_id: str = Field(..., description="Identifiant de la compagnie bénéficiaire de la licence.")
    packages: List[PackageSchema] = Field(..., min_length=1, description="Liste des packages activés pour la compagnie.")
    start_date: Optional[datetime] = Field(default=None, description="Date de début de la licence. Si elle est absente, la date de création est utilisée.")
    end_date: Optional[datetime] = Field(default=None, description="Date de fin de la licence. Elle doit être supérieure à start_date si elle est renseignée.")
    duration_days: Optional[int] = Field(default=None, gt=0, le=3650, description="Durée de la licence en jours lorsque end_date n'est pas fournie.", examples=[365])
    is_active: bool = Field(default=True, description="Indique si la licence est active.")

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateLicenseSchema":
        if self.end_date and self.duration_days:
            raise ValueError("end_date and duration_days cannot be provided together")
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        return self


class UpdateLicenseSchema(BaseModel):
    packages: Optional[List[PackageSchema]] = Field(default=None, min_length=1, description="Nouvelle liste des packages activés pour la compagnie.")
    start_date: Optional[datetime] = Field(default=None, description="Nouvelle date de début de la licence.")
    end_date: Optional[datetime] = Field(default=None, description="Nouvelle date de fin de la licence. Elle doit être supérieure à start_date si elle est renseignée.")
    duration_days: Optional[int] = Field(default=None, gt=0, le=3650, description="Nouvelle durée de la licence en jours.", examples=[365])
    is_active: Optional[bool] = Field(default=None, description="Nouveau statut d'activation de la licence.")

    @model_validator(mode="after")
    def validate_dates(self) -> "UpdateLicenseSchema":
        if self.end_date and self.duration_days:
            raise ValueError("end_date and duration_days cannot be provided together")
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        return self
