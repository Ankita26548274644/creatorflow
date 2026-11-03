from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "CreatorFlow"
    APP_ENV: str = "development"
    UPLOAD_DIR: str = "../uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    MIN_ROWS_FOR_PREDICTION: int = 100
    DATABASE_URL: str
    SECRET_KEY: str
    API_KEY: str = "creatorflow_dev_key"

settings = Settings()

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)