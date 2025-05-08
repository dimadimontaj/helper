from functools import lru_cache
from typing import Protocol
from app.utils.logging import logger
from app.core.settings.transcribe import TranscribeSettings

import httpx
from openai import AsyncOpenAI
from openai.types.audio import Transcription
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class TranscriptionServiceProtocol(Protocol):
    async def transcribe(self, *, file_name: str, file_bytes: bytes, mime: str) -> str: ...


class TranscriptionServiceError(RuntimeError):
    """Высоко‑уровневое исключение сервиса транскрибации."""


@lru_cache(maxsize=1)
def _get_raw_client(settings: TranscribeSettings) -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
    )


class TranscriptionService(TranscriptionServiceProtocol):
    DEFAULT_RETRIES = 3
    RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
        httpx.TimeoutException,
        httpx.NetworkError,
        RuntimeError,
    )

    def __init__(
        self,
        settings: TranscribeSettings,
        client: AsyncOpenAI | None = None,
        *,
        retries: int | None = None,
    ) -> None:
        self._settings = settings
        self._client: AsyncOpenAI = client or _get_raw_client(settings)
        self._retries = retries or self.DEFAULT_RETRIES

    def _retry(self):
        return retry(
            reraise=True,
            stop=stop_after_attempt(self._retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(self.RETRYABLE_EXCEPTIONS),
        )

    async def _safe_transcribe(self, *, file_name: str, file_bytes: bytes, mime: str) -> Transcription:
        @_self_retry := self._retry()
        async def _transcribe():
            return await self._client.audio.transcriptions.create(
                model=self._settings.model,
                file=(file_name, file_bytes, mime),
                language=self._settings.language,
            )

        return await _transcribe()

    async def transcribe(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        mime: str = "audio/ogg",
    ) -> str:
        logger.debug("Calling transcription: model=%s, mime=%s", self._settings.model, mime)
        try:
            resp: Transcription = await self._safe_transcribe(
                file_name=file_name,
                file_bytes=file_bytes,
                mime=mime,
            )
        except Exception as exc:
            logger.exception("Transcription request failed: %s", exc)
            raise TranscriptionServiceError("Ошибка транскрибации аудио") from exc

        if not getattr(resp, "text", None):
            raise TranscriptionServiceError("Сервис не вернул текст транскрибации")

        return resp.text

    async def aclose(self) -> None:
        await self._client.close()

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()
