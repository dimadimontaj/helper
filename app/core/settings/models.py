from pydantic_settings import BaseSettings
from typing_extensions import TypedDict
from typing import Optional


class LLMCodeFormatterSettings(BaseSettings):

    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.1
    top_p: float = 0.9
    max_tokens: int = 600
    seed: int = 12345
    stop: list[str] = ["\\n```"]
    reasoning_effort: str = "low"
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


class GPT_4_1_NANO_Settings(BaseSettings):

    model: str = "openai/gpt-4.1-nano"
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 300
    frequency_penalty: float = 0.1
    presence_penalty: float = 0
    reasoning_effort: Optional[str] = None
    stop: Optional[list[str]] = None
    seed: Optional[int] = None


class GPT_o4_MINI_HIGH_Settings(BaseSettings):

    model: str = "openai/o4-mini-high"
    temperature: float = 0.35
    top_p: float = 0.94
    max_tokens: int = 1800
    reasoning_effort: str = "high"
    frequency_penalty: float = 0.05
    presence_penalty: float = 0.2
    stop: list[str] = ["### Чек‑лист"]
    seed: Optional[int] = None


class GPT_4_1_Settings(BaseSettings):

    model: str = "openai/gpt-4.1"
    temperature: float = 0.3
    top_p: float = 0.95
    max_tokens: int = 2000
    reasoning_effort: Optional[str] = None
    frequency_penalty: float = 0.05
    presence_penalty: float = 0.2
    stop: Optional[list[str]] = None
    seed: Optional[int] = 1234


class LLMModelsMap(TypedDict):
    code_formatter: LLMCodeFormatterSettings
    gpt_4_1_nano: GPT_4_1_NANO_Settings
    o4_mini_high: GPT_o4_MINI_HIGH_Settings
    gpt_4_1: GPT_4_1_Settings











































































# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict
#
#
# class GPT4oMINISettings(BaseSettings):
#
#     model: str = Field("openai/gpt-4o-mini", env="MODEL")
#     temperature: float = Field(0.1, env="TEMPERATURE")
#     top_p: float = Field(0.9, env="TOP_P")
#     max_tokens: int = Field(600, env="MAX_TOKENS")
#     seed: int = Field(12345, env="SEED")
#     stop: list[str] = Field(["```"], env="STOP")
#     reasoning_effort: str = Field("low", env="REASONING_EFFORT")
#
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_prefix="GPT_4O_MINI_",
#         case_sensitive=False,
#         frozen=True,
#         extra="ignore",
#     )
#
#
# class GPT41NANOSettings(BaseSettings):
#
#     model: str = Field("openai/gpt-4.1-nano", env="MODEL")
#     temperature: float = Field(0.2, env="TEMPERATURE")
#     top_p: float = Field(0.9, env="TOP_P")
#     max_tokens: int = Field(300, env="MAX_TOKENS")
#     frequency_penalty: float = Field(0.1, env="FREQUENCY_PENALTY")
#     presence_penalty: float = Field(0, env="PRESENCE_PENALTY")
#
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_prefix="GPT_4_1_NANO_",
#         case_sensitive=False,
#         frozen=True,
#         extra="ignore",
#     )
#
#
# class GPTO4MINIHIGHSettings(BaseSettings):
#
#     model: str = Field("openai/o4-mini-high", env="MODEL")
#     temperature: float = Field(0.35, env="TEMPERATURE")
#     top_p: float = Field(0.94, env="TOP_P")
#     max_tokens: int = Field(1800, env="MAX_TOKENS")
#     reasoning_effort: str = Field("high", env="REASONING_EFFORT")
#     frequency_penalty: float = Field(0.05, env="FREQUENCY_PENALTY")
#     presence_penalty: float = Field(0.2, env="PRESENCE_PENALTY")
#     stop: list[str] = Field(["### Чек‑лист"], env="STOP")
#
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_prefix="GPT_O4_MINI_HIGH_",
#         case_sensitive=False,
#         frozen=True,
#         extra="ignore",
#     )