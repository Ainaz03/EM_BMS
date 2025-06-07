from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_NAM: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    MODE: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
