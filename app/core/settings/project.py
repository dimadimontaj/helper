from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectSettings(BaseSettings):

    name: str = Field("STT Service", env="NAME")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(True, env="DEBUG")
    cors_origins: list[str] = Field(["*"], env="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROJECT_",
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )
