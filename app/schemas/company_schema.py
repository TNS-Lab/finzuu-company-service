from typing import Optional

from pydantic import BaseModel, Field

from app.enums import CompanyType
from app.models.company_model import AddressInfo, CorporationInfo, IdentityInfo


class CompanyBaseSchema(BaseModel):
    name: str
    short_name: str
    type: CompanyType
    industries: str
    sectors: str
    owner: IdentityInfo
    address: AddressInfo
    corporation: Optional[CorporationInfo] = None
    self_sharing: Optional[float] = Field(default=None, ge=0)
    is_active: bool = True


class CreateCompanySchema(CompanyBaseSchema):
    admin_email: str
    admin_first_name: str
    admin_last_name: str


class UpdateCompanySchema(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    type: Optional[CompanyType] = None
    industries: Optional[str] = None
    sectors: Optional[str] = None
    owner: Optional[IdentityInfo] = None
    address: Optional[AddressInfo] = None
    corporation: Optional[CorporationInfo] = None
    self_sharing: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
