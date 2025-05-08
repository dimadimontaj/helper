from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TranscribeSettings(BaseSettings):

    model: str = Field("whisper-1", env="MODEL")
    language: str = Field("ru", env="LANGUAGE")
    api_key: str = Field("your api key", env="API_KEY")
    base_url: str = Field("https://api.nexara.ru/api/v1", env="BASE_URL")
    timeout: int = Field(15, env="TIMEOUT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TRANSCRIBE_",
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )
