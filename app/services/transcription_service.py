import asyncio
import random
from typing import AsyncIterator, List, Protocol

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)

from app.core.config import TranscribeSettings
from app.utils.logging import logger


class TranscriptionServiceError(Exception):
    """Fatal Deepgram‑related failure."""


class TranscriptionServiceProtocol(Protocol):
    async def feed(self, chunk: bytes) -> None: ...
    async def transcripts(self) -> AsyncIterator[str]: ...
    async def stop(self) -> None: ...


class TranscriptionService:
    MAX_FRAME = 8192

    def __init__(self, cfg: TranscribeSettings):
        self._cfg = cfg

        self._dg = DeepgramClient(
            cfg.api_key,
            DeepgramClientOptions(options={
                "keep_alive": "true",
                "auto_flush_reply_delta": 8000,
            }),
        )
        self._ws = self._dg.listen.asyncwebsocket.v("1")

        self._q: asyncio.Queue[str | None] = asyncio.Queue(32)
        self._buf: List[str] = []
        self._closed = asyncio.Event()

        # события
        self._ws.on(LiveTranscriptionEvents.Open, self._on_open)
        self._ws.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
        self._ws.on(LiveTranscriptionEvents.Close, self._on_close)
        self._ws.on(LiveTranscriptionEvents.Error, self._on_error)

        self._opts = LiveOptions(
            model=cfg.model,
            language=cfg.language,
            encoding="linear16",
            sample_rate=cfg.sample_rate,
            channels=cfg.channels,
            interim_results=True,
            vad_events=True,
            smart_format=True,
            endpointing=cfg.endpointing_ms,
            utterance_end_ms=cfg.utterance_end_ms,
        )
        self._addons = {"no_delay": "true"}

    # --------------- контекст-менеджер ---------------
    async def __aenter__(self):
        await self._start()
        return self

    async def __aexit__(self, *_):
        await self.stop()

    # ---------------- публичное API ------------------
    async def feed(self, pcm: bytes):
        if self._closed.is_set():
            raise TranscriptionServiceError("stream closed")
        for off in range(0, len(pcm), self.MAX_FRAME):
            await self._ws.send(pcm[off:off + self.MAX_FRAME])

    async def transcripts(self) -> AsyncIterator[str]:
        while (txt := await self._q.get()) is not None:
            yield txt

    async def stop(self):
        if not self._closed.is_set():
            try:
                await self._ws.send('{"type":"CloseStream"}')
            finally:
                await self._ws.finish()
                await self._closed.wait()

    # ------------------- внутреннее ------------------
    async def _start(self):
        try:
            if await self._ws.start(self._opts, addons=self._addons):
                return
        except Exception as e:
            logger.exception("DG error: %s", e)
            raise TranscriptionServiceError("DG connect failed") from e

    async def _on_open(self, _, open, **kwargs):
        logger.debug("DG open connection")

    async def _on_transcript(self, _, result, **kwargs):
        txt = result.channel.alternatives[0].transcript
        if not txt:
            return
        if result.is_final:
            self._buf.append(txt)
            if result.speech_final:
                await self._q.put(" ".join(self._buf))
                self._buf.clear()

    async def _on_close(self, _, close, **kwargs):
        await self._q.put(None)
        self._closed.set()

    async def _on_error(self, error, **_):
        logger.exception("DG error:", error)
        raise TranscriptionServiceError(RuntimeError(error))
