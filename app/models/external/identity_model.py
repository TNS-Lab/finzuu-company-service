from pydantic import BaseModel


class IdentityInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
