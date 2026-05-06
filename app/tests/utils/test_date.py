from datetime import datetime, timedelta, timezone

from app.utils.date import add_days, add_minutes, add_months, has_expired


def test_add_minutes():
    date = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    assert add_minutes(date, 15) == datetime(2026, 5, 6, 10, 15, tzinfo=timezone.utc)


def test_add_months():
    date = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    assert add_months(date, 2) == datetime(2026, 7, 6, 10, 0, tzinfo=timezone.utc)


def test_add_days():
    date = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    assert add_days(date, 10) == datetime(2026, 5, 16, 10, 0, tzinfo=timezone.utc)


def test_has_expired():
    assert has_expired(datetime.now(timezone.utc) - timedelta(days=1)) is True
    assert has_expired(datetime.now(timezone.utc) + timedelta(days=1)) is False
    assert has_expired(None) is False
