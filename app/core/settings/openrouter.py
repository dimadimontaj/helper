from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenrouterSettings(BaseSettings):

    base_url: str = Field("https://openrouter.ai/api/v1", env="BASE_URL")
    api_key: str = Field("your api key", env="API_KEY")
    timeout: int = Field(60, env="TIMEOUT")
    max_keepalive_connections: int = Field(20, env="MAX_KEEPALIVE_CONNECTIONS")
    max_connections: int = Field(40, env="MAX_CONNECTIONS")
    keepalive_expiry: int = Field(60, env="KEEPALIVE_EXPIRY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OPENROUTER_",
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )
