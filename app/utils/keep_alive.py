import asyncio
from typing import Optional
from app.services.llm_service import LLMServiceProtocol
from app.core.settings.base import OpenrouterSettings
from app.utils.logging import logger
from typing import Protocol


class KeepAliveProtocol(Protocol):
    async def start(self): ...
    async def stop(self, task: asyncio.Task): ...


class KeepAlive(KeepAliveProtocol):
    def __init__(self, llm: LLMServiceProtocol, settings: OpenrouterSettings):
        self.llm = llm
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()
        self._ping_interval: int = settings.keepalive_expiry - 15

    async def _ping_loop(self):
        messages = [{"role": "user", "content": "ping"}]
        while not self._stop.is_set():
            try:
                await self.llm.query_llm(model="gpt_4_1_nano", messages=messages)
                logger.info("Keep-alive ping succeeded")
            except Exception as exc:
                logger.warning("Keep-alive ping failed: %s", exc)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self._ping_interval)
            except asyncio.TimeoutError:
                continue

    async def start(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._ping_loop())
        return self._task

    async def stop(self, task: asyncio.Task):
        self._stop.set()
        await task
