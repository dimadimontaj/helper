import asyncio
from typing import AsyncIterator

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.dependencies import get_transcription_service
from app.services.transcription_service import (
    TranscriptionServiceError,
    TranscriptionServiceProtocol,
)
from app.utils.logging import logger

router = APIRouter()


async def _forward(ws: WebSocket, gen: AsyncIterator[str]):
    try:
        async for sentence in gen:
            logger.info(sentence)
            await ws.send_text(sentence)
    except asyncio.CancelledError:
        return


@router.websocket("/")
async def transcribe(
    ws: WebSocket,
    transcription: TranscriptionServiceProtocol = Depends(get_transcription_service),
):
    logger.info("/transcribe connected")

    await ws.accept()
    async with transcription as dg:
        forward_task = asyncio.create_task(_forward(ws, dg.transcripts()), name="forward")
        try:
            while True:
                try:
                    data = await ws.receive_bytes()
                except WebSocketDisconnect:
                    logger.info("client disconnected")
                    break
                try:
                    await dg.feed(data)
                except TranscriptionServiceError as exc:
                    logger.error("feed error: %s", exc)
                    await ws.close(code=1011, reason="transcription error")
                    break
        finally:
            forward_task.cancel()
            await asyncio.gather(forward_task, return_exceptions=True)
            logger.info("cleanup done")
