from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from app.configs.config import settings
from app.models import company_model, license_model


DATABASE_URL = f"{settings.DB_CONNECTION}://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"


async def initiate_database():
    client = AsyncMongoMockClient(DATABASE_URL)
    test_database = client.get_database()

    original_list_collection_names = test_database.list_collection_names

    async def list_collection_names(*args, **kwargs):
        return await original_list_collection_names()

    test_database.list_collection_names = list_collection_names
    await init_beanie(
        database=test_database,
        document_models=[
            company_model.Company,
            license_model.License,
        ],
    )
