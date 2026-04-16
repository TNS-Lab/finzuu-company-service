from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def add_minutes(date: datetime = None, minutes: int = 5) -> datetime:
    """Ajoute des minutes à une date"""
    if date is None:
        date = datetime.now(timezone.utc)
        
    return date + relativedelta(minutes=minutes)

def add_months(date: datetime = None, months: int = 1) -> datetime:
    """Ajoute des mois à une date"""
    if date is None:
        date = datetime.now(timezone.utc)

    return date + relativedelta(months=months)


def add_days(date: datetime = None, days: int = 1) -> datetime:
    """Ajoute des jours a une date."""
    if date is None:
        date = datetime.now(timezone.utc)

    return date + relativedelta(days=days)


def has_expired(date: datetime | None) -> bool:
    """Indique si une date d'expiration est depassee."""
    if date is None:
        return False

    reference = date if date.tzinfo else date.replace(tzinfo=timezone.utc)
    return reference < datetime.now(timezone.utc)
