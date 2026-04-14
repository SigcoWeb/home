from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MODO_DEPLOY: str = "cloud"          # "cloud" | "local"
    ENTORNO: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://sgc:sgc@localhost:5432/sigcoweb"
    DATABASE_URL_SYNC: str = "postgresql://sgc:sgc@localhost:5432/sigcoweb"

    SECRET_KEY: str = "cambiar-en-produccion-usar-secrets-token-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    APP_NOMBRE: str = "sigcoWeb"
    APP_VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
