import uvicorn
from app.configs.config import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=12041, reload=settings.APP_ENV != "production")
