from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field

from app.enums import PackageName
from app.models.time_stamped_model import TimeStampedDocument


class CompanySnapshot(BaseModel):
    id: str
    name: str
    short_name: str


class PackageInfo(BaseModel):
    name: PackageName
    description: str


class License(TimeStampedDocument):
    id: str = Field(default_factory=lambda: str(uuid4()))
    start_date: datetime
    end_date: datetime
    company: CompanySnapshot
    packages: List[PackageInfo]
    is_active: bool = True

    class Settings:
        name = "licenses"
        use_state_management = True
