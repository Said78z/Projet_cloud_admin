from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/movielens"
    REDIS_URL: str = "redis://redis:6379"
    CACHE_TTL: int = 300  # seconds

    class Config:
        env_file = ".env"


settings = Settings()
