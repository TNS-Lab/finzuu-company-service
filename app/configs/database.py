from beanie import init_beanie
from pymongo import AsyncMongoClient
import urllib.parse

from .config import settings
from app.models import company_model, license_model


if settings.DB_WITH_AUTH:
    db_user_escaped = urllib.parse.quote_plus(settings.DB_USERNAME)
    db_pass_escaped = urllib.parse.quote_plus(settings.DB_PASSWORD)

    DATABASE_URL = f"{settings.DB_CONNECTION}://{db_user_escaped}:{db_pass_escaped}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
else:
    DATABASE_URL = f"{settings.DB_CONNECTION}://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

async def initiate_database():
    client = AsyncMongoClient(DATABASE_URL)

    await init_beanie(
        database=client.get_database(),
        document_models=[
            company_model.Company,
            license_model.License,
        ]
    )
