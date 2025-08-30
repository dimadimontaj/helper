from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Optional

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
        env_prefix="PROJECT_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )


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
        env_prefix="TRANSCRIBE_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )


class OpenRouterSettings(BaseSettings):
    base_url: str = Field("https://openrouter.ai/api/v1", env="BASE_URL")
    api_key: str = Field("123", env="API_KEY")
    timeout: int = Field(60, env="TIMEOUT")
    max_keepalive_connections: int = Field(20, env="MAX_KEEPALIVE_CONNECTIONS")
    max_connections: int = Field(40, env="MAX_CONNECTIONS")
    keepalive_expiry: int = Field(60, env="KEEPALIVE_EXPIRY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPENROUTER_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )


class LLMSettings(BaseSettings):
    """База для любой LLM-модели. Без усложнений."""
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    reasoning_effort: Optional[str]
    stop: Optional[list[str]]
    seed: Optional[int]


class GPT_4_1_NANO(LLMSettings):
    model: str = "openai/gpt-4.1-nano"
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 300
    frequency_penalty: float = 0.1
    presence_penalty: float = 0
    reasoning_effort: Optional[str] = None
    stop: Optional[list[str]] = None
    seed: Optional[int] = None


LLMModelsMap = Dict[str, LLMSettings]


def _build_llm_models() -> LLMModelsMap:
    return {
        "gpt_4_1_nano": GPT_4_1_NANO(),
    }


class AppSettings(BaseSettings):
    project: ProjectSettings = Field(default_factory=ProjectSettings)
    transcribe: TranscribeSettings = Field(default_factory=TranscribeSettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    llm_models: LLMModelsMap = Field(default_factory=_build_llm_models)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Глобальная точка входа для конфигов (с кэшированием)."""
    return AppSettings()
