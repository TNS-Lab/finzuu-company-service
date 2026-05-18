from enum import Enum


class AppEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class Permission(AppEnum):
    COMPANY_READ = "COMPANY-READ"
    COMPANY_CREATE = "COMPANY-CREATE"
    COMPANY_UPDATE = "COMPANY-UPDATE"

    LICENSE_READ = "LICENSE-READ"
    LICENSE_CREATE = "LICENSE-CREATE"
    LICENSE_UPDATE = "LICENSE-UPDATE"


class PackageName(AppEnum):
    ALL = "ALL"
    READY_CASH = "READY_CASH"
    READY_COLLECTE = "READY_COLLECTE"
    BULK = "BULK"


class CompanyType(AppEnum):
    MERCHANT = "MERCHANT"
    BANK = "BANK"
    IMF = "IMF"
    AGENCY = "AGENCY"
    KIOSK = "KIOSK"
    FUNDING_PROVIDER = "FUNDING_PROVIDER"
    FONDATION = "FONDATION"
