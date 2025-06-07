from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    REDIS_HOST: str
    REDIS_PORT: int

    MODE: str
    SECRET_KEY: str
    JWT_LIFETIME_SECONDS: int = 3600

    class Config:
        # Абсолютный путь до .env, независимо от cwd
        env_file = str(Path(__file__).parents[2] / ".env")
        env_file_encoding = "utf-8"

    @property
    def DATABASE_URL(self) -> str:
        # синхронный URL для Alembic
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

# глобальный экземпляр
settings = Settings()
