from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.enums import CompanyType
from app.models.external.identity_model import IdentityInfo
from app.models.time_stamped_model import TimeStampedDocument


class AddressInfo(BaseModel):
    address_line_1: str = Field(..., description="Primary address line")
    address_line_2: str | None = Field(default=None, description="Secondary address line")
    street_number: str | None = Field(default=None, description="Street number")
    street_name: str = Field(..., description="Street name")
    postal_code: str | None = Field(default=None, description="Postal code")
    city: str | None = Field(default=None, description="City")
    region: str | None = Field(default=None, description="Region or state")
    country: str = Field(..., description="Country code or country name")
    latitude: float | None = Field(default=None, description="Latitude")
    longitude: float | None = Field(default=None, description="Longitude")


class CorporationInfo(BaseModel):
    id: str
    name: str
    short_name: str


class Company(TimeStampedDocument):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    short_name: str
    type: CompanyType
    industries: List[str]
    sectors: List[str]
    owner: IdentityInfo
    address: AddressInfo
    corporation: Optional[CorporationInfo] = None
    self_sharing: Optional[float] = None
    is_active: bool = True

    @field_validator("industries", "sectors", mode="before")
    @classmethod
    def normalize_string_list(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    class Settings:
        name = "companies"
        use_state_management = True
