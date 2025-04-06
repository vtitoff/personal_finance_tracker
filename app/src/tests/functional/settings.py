from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".test.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    postgres_url: str = Field(
        "postgresql+asyncpg://user:password@postgres:5432/test_db",
        alias="TEST_POSTGRES_URL",
    )
    redis_port: str = Field("6379", alias="REDIS_PORT")
    redis_host: str = Field("redis", alias="REDIS_HOST")
    service_url: str = Field("http://localhost:8000", alias="SERVICE_URL")
    jwt_secret_key: str = Field("my_secret_key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_exp_hours: int = Field(5, alias="ACCESS_TOKEN_EXPIRATION_HOURS")


settings = Settings()
