from beanie import init_beanie
from pymongo import AsyncMongoClient

from .config import settings
from app.models import company_model, license_model


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
