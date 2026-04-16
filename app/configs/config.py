import os
from pydantic.v1 import BaseSettings


dir_path = os.path.dirname(os.path.realpath(__file__))

class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str
    APP_DESCRIPTION: str = "Company service"

    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_CONNECTION: str

    DEFAULT_LICENSE_DURATION_DAYS: int = 365
    USER_SERVICE_BASE_URL: str = ""
    ACCOUNT_SERVICE_BASE_URL: str = ""
    NOTIFICATION_SERVICE_BASE_URL: str = ""

    class Config:
        env_file = './.env'

settings = Settings()
