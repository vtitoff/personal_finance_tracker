from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    access_token_exp_hours: int = Field(5, alias="ACCESS_TOKEN_EXPIRATION_HOURS")
    project_name: str = Field("Personal Finance Tracker", alias="PROJECT_NAME")
    postgres_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/foo", alias="POSTGRES_URL"
    )
    engine_echo: bool = Field(False, alias="ENGINE_ECHO")
    jwt_secret_key: str = Field("my_secret_key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    redis_port: str = Field("6379", alias="REDIS_PORT")
    redis_host: str = Field("redis", alias="REDIS_HOST")


settings = Settings()
