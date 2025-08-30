from app.services.transcription_service import TranscriptionService
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService

from fastapi import Depends
from .config import get_settings, AppSettings
from app.utils.keep_alive import KeepAlive


def get_app_settings(
    settings: AppSettings = get_settings(),
) -> AppSettings:
    return settings


def get_llm_service(
    settings: AppSettings = Depends(get_app_settings)
) -> LLMService:
    return LLMService(settings)


def get_prompt_service() -> PromptService:
    return PromptService()


def get_keep_alive(
    llm: LLMService = get_llm_service(get_app_settings()),
    settings: AppSettings = get_app_settings(),
) -> KeepAlive:
    return KeepAlive(llm, settings.openrouter)


def get_transcription_service(
    settings: AppSettings = Depends(get_app_settings),
) -> TranscriptionService:
    return TranscriptionService(settings.transcribe)
