from functools import lru_cache
from typing import Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    load and validate the environment variables / .env file using the pydantic settings
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    # postgres components (used to build DATABASE_URL if not set directly)
    DB_USER: str = "lsa_user"
    DB_PASSWORD: str = "lsa_password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "lsa_db"

    #optional fields
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    MOCK_PAYMENT_API_URL: Optional[str] = "http://localhost:5000/api/v1/mock/payment/"
    MOCK_API_TIMEOUT_SECONDS: Optional[int] = 5
    
    LOG_LEVEL: str = "INFO"

    # properties to build the DB URI for the postgres credentials
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> str:
        if self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}_test"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached so .env is parsed once per process and not on every access."""
    return Settings()