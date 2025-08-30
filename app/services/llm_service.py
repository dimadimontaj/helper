from functools import lru_cache
from typing import Protocol, Sequence, Any, AsyncIterable

import httpx
from pydantic import BaseModel
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from app.core.config import AppSettings, OpenRouterSettings, LLMModelsMap
from app.utils.logging import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.schemas.schemas import ChatMessage


class LLMServiceProtocol(Protocol):
    async def query_llm(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
    ) -> str: ...

    async def stream_query_llm(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
    ) -> AsyncIterable[str]: ...


class LLMServiceError(RuntimeError):
    """Высоко‑уровневая ошибка LLM‑сервиса."""


@lru_cache(maxsize=8)
def _get_raw_client(settings: OpenRouterSettings | None) -> AsyncOpenAI:
    transport = httpx.AsyncHTTPTransport(
        http2=True,
        limits=httpx.Limits(
            max_keepalive_connections=settings.max_keepalive_connections,
            max_connections=settings.max_connections,
            keepalive_expiry=settings.keepalive_expiry,
        ),
    )

    http_client = httpx.AsyncClient(
        transport=transport,
        timeout=settings.timeout,
    )

    return AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        http_client=http_client,
    )


class LLMService(LLMServiceProtocol):
    DEFAULT_RETRIES = 3
    RETRYABLE_EXCEPTIONS = (
        httpx.TimeoutException,
        httpx.NetworkError,
        RuntimeError,
    )

    def __init__(
        self,
        settings: AppSettings | None = None,
        client: AsyncOpenAI | None = None,
        *,
        retries: int | None = None,
    ) -> None:
        self._client: AsyncOpenAI = client or _get_raw_client(settings.openrouter)
        self._retries = retries or self.DEFAULT_RETRIES
        self._models: LLMModelsMap = settings.llm_models

    def _build_api_params(
        self,
        model: str,
        messages: Sequence[ChatMessage],
    ) -> dict[str, Any]:

        cfg = self._get_model_cfg(model)

        params: dict[str, Any] = {
            "model": cfg.model,
            "messages": messages,
        }
        optional_map = {
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "max_tokens": cfg.max_tokens,
            "seed": cfg.seed,
            "stop": cfg.stop,
            "reasoning_effort": cfg.reasoning_effort,
            "frequency_penalty": cfg.frequency_penalty,
            "presence_penalty": cfg.presence_penalty,
        }
        params.update({k: v for k, v in optional_map.items() if v is not None})
        return params

    def _retry(self):
        return retry(
            reraise=True,
            stop=stop_after_attempt(self._retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(self.RETRYABLE_EXCEPTIONS),
        )

    async def _safe_request(self, **api_params: Any) -> ChatCompletion:
        @_self_retry := self._retry()
        async def _query_llm():
            return await self._client.chat.completions.create(**api_params)

        return await _query_llm()

    def _get_model_cfg(self, name: str) -> BaseModel:
        try:
            return self._models[name]
        except Exception as exc:
            logger.exception("LLM model not found: %s", exc)
            raise LLMServiceError("LLM model not found") from exc

    async def query_llm(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
    ) -> str:
        logger.debug("Calling LLM: model=%s, messages_count=%d", model, len(messages))

        api_params = self._build_api_params(
            model,
            messages,
        )

        try:
            resp: ChatCompletion = await self._safe_request(**api_params)
        except Exception as exc:
            logger.exception("LLM request failed: %s", exc)
            raise LLMServiceError("LLM request failed") from exc

        if not resp.choices:
            raise LLMServiceError("LLM response has no choices")

        return resp.choices[0].message.content

    async def stream_query_llm(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
    ) -> AsyncIterable[str]:
        logger.debug("Calling LLM: model=%s, messages_count=%d", model, len(messages))

        api_params = self._build_api_params(
            model,
            messages,
        )

        api_params["stream"] = True

        try:
            stream: AsyncStream[ChatCompletionChunk] = await self._client.chat.completions.create(**api_params)
        except Exception as exc:
            logger.exception("LLM request failed: %s", exc)
            raise LLMServiceError("LLM request failed") from exc

        try:
            buffer = []
            async for chunk in stream:
                delta = getattr(chunk.choices[0].delta, "content", "")
                if delta:
                    buffer.append(delta)
                    if len(buffer) >= 3 or delta.endswith(("\n", ".", "?", "!")):
                        data = "".join(buffer)
                        buffer.clear()
                        yield f"data: {data}\n\n"
        except Exception as exc:
            logger.exception("Error while streaming LLM response")
            raise LLMServiceError("Error while streaming LLM response") from exc

    async def aclose(self) -> None:
        await self._client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()















































































# from functools import lru_cache
# from typing import Protocol, Sequence, Any
#
# import httpx
# from openai import AsyncOpenAI
# from openai.types.chat import ChatCompletion
# from app.core.settings.openrouter import OpenrouterSettings
# from app.utils.logging import logger
# from tenacity import (
#     retry,
#     stop_after_attempt,
#     wait_exponential,
#     retry_if_exception_type,
# )
# from app.schemas.schemas import ChatMessage
#
#
# class LLMServiceProtocol(Protocol):
#     async def query_llm(
#         self,
#         *,
#         model: str,
#         messages: Sequence[ChatMessage],
#         temperature: float | None = None,
#         top_p: float | None = None,
#         max_tokens: int | None = None,
#         seed: int | None = None,
#         stop: Sequence[str] | None = None,
#         reasoning_effort: str | None = None,
#         frequency_penalty: float | None = None,
#         presence_penalty: float | None = None,
#     ) -> str: ...
#
#
# class LLMServiceError(RuntimeError):
#     """Высоко‑уровневая ошибка LLM‑сервиса."""
#
#
# @lru_cache(maxsize=1)
# def _get_raw_client(settings: OpenrouterSettings | None) -> AsyncOpenAI:
#     return AsyncOpenAI(
#         base_url=settings.base_url,
#         api_key=settings.api_key,
#         timeout=settings.timeout,
#     )
#
#
# class LLMService(LLMServiceProtocol):
#     DEFAULT_RETRIES = 3
#     RETRYABLE_EXCEPTIONS = (
#         httpx.TimeoutException,
#         httpx.NetworkError,
#         RuntimeError,
#     )
#
#     def __init__(
#         self,
#         settings: OpenrouterSettings | None = None,
#         client: AsyncOpenAI | None = None,
#         *,
#         retries: int | None = None,
#     ) -> None:
#         self._client: AsyncOpenAI = client or _get_raw_client(settings)
#         self._retries = retries or self.DEFAULT_RETRIES
#
#     @staticmethod
#     def _build_api_params(
#         model: str,
#         messages: Sequence[ChatMessage],
#         temperature: float | None,
#         top_p: float | None,
#         max_tokens: int | None,
#         seed: int | None,
#         stop: Sequence[str] | None,
#         reasoning_effort: str | None,
#         frequency_penalty: float | None,
#         presence_penalty: float | None,
#     ) -> dict[str, Any]:
#         params: dict[str, Any] = {
#             "model": model,
#             "messages": messages,
#         }
#         optional_map = {
#             "temperature": temperature,
#             "top_p": top_p,
#             "max_tokens": max_tokens,
#             "seed": seed,
#             "stop": stop,
#             "reasoning_effort": reasoning_effort,
#             "frequency_penalty": frequency_penalty,
#             "presence_penalty": presence_penalty,
#         }
#         params.update({k: v for k, v in optional_map.items() if v is not None})
#         return params
#
#     def _retry(self):
#         return retry(
#             reraise=True,
#             stop=stop_after_attempt(self._retries),
#             wait=wait_exponential(multiplier=1, min=1, max=10),
#             retry=retry_if_exception_type(self.RETRYABLE_EXCEPTIONS),
#         )
#
#     async def _safe_request(self, **api_params: Any) -> ChatCompletion:
#         @_self_retry := self._retry()
#         async def _query_llm():
#             return await self._client.chat.completions.create(**api_params)
#
#         return await _query_llm()
#
#     async def query_llm(
#         self,
#         *,
#         model: str,
#         messages: Sequence[ChatMessage],
#         temperature: float | None = None,
#         top_p: float | None = None,
#         max_tokens: int | None = None,
#         seed: int | None = None,
#         stop: Sequence[str] | None = None,
#         reasoning_effort: str | None = None,
#         frequency_penalty: float | None = None,
#         presence_penalty: float | None = None,
#     ) -> str:
#         logger.debug("Calling LLM: model=%s, messages_count=%d", model, len(messages))
#
#         api_params = self._build_api_params(
#             model,
#             messages,
#             temperature,
#             top_p,
#             max_tokens,
#             seed,
#             stop,
#             reasoning_effort,
#             frequency_penalty,
#             presence_penalty,
#         )
#
#         try:
#             resp: ChatCompletion = await self._safe_request(**api_params)
#         except Exception as exc:
#             logger.exception("LLM request failed: %s", exc)
#             raise LLMServiceError("LLM request failed") from exc
#
#         if not resp.choices:
#             raise LLMServiceError("LLM response has no choices")
#
#         return resp.choices[0].message.content
#
#     async def aclose(self) -> None:
#         await self._client.close()
#
#     async def __aenter__(self):
#         return self
#
#     async def __aexit__(self, exc_type, exc, tb):
#         await self.aclose()
