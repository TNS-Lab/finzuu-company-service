from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.enums import CompanyType
from app.models.company_model import AddressInfo, CorporationInfo, IdentityInfo


class CompanyBaseSchema(BaseModel):
    name: str = Field(..., description="Nom légal ou commercial de la compagnie.", examples=["FinZuu Merchant Cameroon"])
    short_name: str = Field(..., description="Nom court unique utilisé pour l'affichage et les libellés de compte.", examples=["FZMC"])
    type: CompanyType = Field(..., description="Catégorie métier de la compagnie.")
    industries: List[str] = Field(..., min_length=1, description="Liste des industries dans lesquelles la compagnie opère.", examples=[["Finance", "Retail"]])
    sectors: List[str] = Field(..., min_length=1, description="Liste des secteurs d'activité couverts par la compagnie.", examples=[["Payments", "Mobile Money"]])
    owner: IdentityInfo = Field(..., description="Informations d'identité et de contact du propriétaire ou représentant légal.")
    address: AddressInfo = Field(..., description="Adresse physique de la compagnie.")
    corporation: Optional[CorporationInfo] = Field(default=None, description="Informations de la corporation parente si la compagnie y est rattachée.")
    self_sharing: Optional[float] = Field(default=None, ge=0, description="Taux ou montant de self-sharing configuré pour la compagnie.", examples=[0])
    is_active: bool = Field(default=True, description="Indique si la compagnie est active.")

    @field_validator("industries", "sectors", mode="before")
    @classmethod
    def normalize_string_list(cls, value):
        if isinstance(value, str):
            values = [item.strip() for item in value.split(",") if item.strip()]
            return values or [value]
        return value


class CreateCompanySchema(CompanyBaseSchema):
    admin_email: str = Field(..., description="Email de l'utilisateur administrateur COMPANY à créer pour cette compagnie.", examples=["admin.company@finzuu.com"])
    admin_first_name: str = Field(..., description="Prénom de l'utilisateur administrateur COMPANY.", examples=["Marie"])
    admin_last_name: str = Field(..., description="Nom de l'utilisateur administrateur COMPANY.", examples=["Kamga"])


class UpdateCompanySchema(BaseModel):
    name: Optional[str] = Field(default=None, description="Nouveau nom légal ou commercial de la compagnie.")
    short_name: Optional[str] = Field(default=None, description="Nouveau nom court de la compagnie.")
    type: Optional[CompanyType] = Field(default=None, description="Nouvelle catégorie métier de la compagnie.")
    industries: Optional[List[str]] = Field(default=None, description="Nouvelle liste des industries de la compagnie.")
    sectors: Optional[List[str]] = Field(default=None, description="Nouvelle liste des secteurs d'activité de la compagnie.")
    owner: Optional[IdentityInfo] = Field(default=None, description="Nouvelles informations du propriétaire ou représentant légal.")
    address: Optional[AddressInfo] = Field(default=None, description="Nouvelle adresse de la compagnie.")
    corporation: Optional[CorporationInfo] = Field(default=None, description="Nouvelles informations de corporation parente.")
    self_sharing: Optional[float] = Field(default=None, ge=0, description="Nouveau taux ou montant de self-sharing.")
    is_active: Optional[bool] = Field(default=None, description="Nouveau statut d'activation de la compagnie.")

    @field_validator("industries", "sectors", mode="before")
    @classmethod
    def normalize_string_list(cls, value):
        if isinstance(value, str):
            values = [item.strip() for item in value.split(",") if item.strip()]
            return values or [value]
        return value
