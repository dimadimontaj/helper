from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TranscribeSettings(BaseSettings):

    model: str = Field("nova-3", env="MODEL")
    language: str = Field("multi", env="LANGUAGE")
    api_key: str = Field("your api key", env="API_KEY")
    sample_rate: int = Field(16_000, env="SAMPLE_RATE")
    channels: int = Field(1, env="CHANNELS")
    endpointing_ms: int = Field(1_000, env="ENDPOINTING_MS")
    utterance_end_ms: str = Field("1000", env="UTTERANCE_END_MS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TRANSCRIBE_",
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )
