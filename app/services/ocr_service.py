from typing import Protocol, Any, Sequence
import json
from app.utils.logging import logger
from app.core.settings.ocr import OCRSettings

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class OCRServiceProtocol(Protocol):
    async def parse_image(self, *, file_bytes: bytes, file_name: str) -> str: ...


class OCRServiceError(RuntimeError):
    """Исключение бизнес‑уровня, скрывает детали HTTP слоя."""


class OCRService(OCRServiceProtocol):
    DEFAULT_RETRIES = 3
    RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
        httpx.TimeoutException,
        httpx.NetworkError,
        httpx.HTTPStatusError,
    )

    def __init__(
        self,
        settings: OCRSettings,
        client: httpx.AsyncClient | None = None,
        *,
        retries: int | None = None,
    ) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient = client or httpx.AsyncClient(timeout=settings.timeout)
        self._retries = retries or self.DEFAULT_RETRIES

    def _build_payload(self) -> dict[str, Any]:
        return {
            "apikey": self._settings.api_key,
            "language": self._settings.language,
            "isOverlayRequired": False,
            "OCREngine": self._settings.engine,
            "scale": self._settings.scale,
        }

    @staticmethod
    def _build_files(file_bytes: bytes, file_name: str) -> dict[str, tuple[str, bytes, str]]:
        return {"file": (file_name, file_bytes, "application/octet-stream")}

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        parsed_results: Sequence[dict[str, Any]] = data.get("ParsedResults", [])
        if not parsed_results:
            raise OCRServiceError("OCR вернул пустой список ParsedResults")
        text = parsed_results[0].get("ParsedText", "").strip()
        if not text:
            raise OCRServiceError("OCR не смог распознать текст")
        return text

    def _retry(self):
        return retry(
            reraise=True,
            stop=stop_after_attempt(self._retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(self.RETRYABLE_EXCEPTIONS),
        )

    async def _safe_post(self, *, data: dict[str, Any], files: dict[str, Any]) -> httpx.Response:
        @_self_retry := self._retry()
        async def _post():
            resp = await self._client.post(self._settings.base_url, data=data, files=files)
            resp.raise_for_status()
            return resp

        return await _post()

    async def parse_image(self, *, file_bytes: bytes, file_name: str) -> str:
        payload = self._build_payload()
        files = self._build_files(file_bytes, file_name)

        logger.debug("Calling OCR: file=%s, language=%s", file_name, payload["language"])

        resp = await self._safe_post(data=payload, files=files)

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise OCRServiceError(f"Невалидный JSON от OCR: {exc}") from exc

        return self._extract_text(data)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()