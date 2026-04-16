import uvicorn
from app.configs.config import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=12041, reload=settings.APP_ENV != "production")
