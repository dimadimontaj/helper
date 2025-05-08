import uuid

import structlog
from fastapi import Request

from app.utils.logging import logger


async def add_request_id(request: Request, call_next):
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request.headers.get("X-Request-ID", str(uuid.uuid4())),
        path=request.url.path,
        method=request.method,
        client=request.client.host,
    )
    response = await call_next(request)
    logger.info("response", status=response.status_code)
    return response
