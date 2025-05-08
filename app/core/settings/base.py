from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from .models import LLMModelsMap, LLMCodeFormatterSettings, GPT_4_1_NANO_Settings, GPT_o4_MINI_HIGH_Settings, GPT_4_1_Settings
from .transcribe import TranscribeSettings
from .ocr import OCRSettings
from .openrouter import OpenrouterSettings
from .project import ProjectSettings


class AppSettings(BaseSettings):
    llm_models: LLMModelsMap = {
        "code_formatter": LLMCodeFormatterSettings(),
        "gpt_4_1_nano": GPT_4_1_NANO_Settings(),
        "o4_mini_high": GPT_o4_MINI_HIGH_Settings(),
        "gpt_4_1": GPT_4_1_Settings(),
    }
    transcribe: TranscribeSettings = Field(default_factory=TranscribeSettings)
    ocr: OCRSettings = Field(default_factory=OCRSettings)
    openrouter: OpenrouterSettings = Field(default_factory=OpenrouterSettings)
    project: ProjectSettings = Field(default_factory=ProjectSettings)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
