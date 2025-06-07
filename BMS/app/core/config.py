from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    MODE: str

    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
