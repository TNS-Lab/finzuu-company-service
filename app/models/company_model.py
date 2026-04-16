from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.enums import CompanyType
from app.models.time_stamped_model import TimeStampedDocument


class IdentityInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    identity_number: str | None = None


class AddressInfo(BaseModel):
    address_line_1: str
    address_line_2: str | None = None
    street_number: str | None = None
    street_name: str
    postal_code: str | None = None
    city: str | None = None
    region: str | None = None
    country: str
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CorporationInfo(BaseModel):
    id: str
    name: str
    short_name: str


class Company(TimeStampedDocument):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    short_name: str
    type: CompanyType
    industries: str
    sectors: str
    owner: IdentityInfo
    address: AddressInfo
    corporation: Optional[CorporationInfo] = None
    self_sharing: Optional[float] = None
    is_active: bool = True

    class Settings:
        name = "companies"
        use_state_management = True
