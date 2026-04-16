from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.enums import PackageName


class PackageSchema(BaseModel):
    name: PackageName
    description: str


class CreateLicenseSchema(BaseModel):
    company_id: str
    packages: List[PackageSchema]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = Field(default=None, gt=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateLicenseSchema":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        return self
