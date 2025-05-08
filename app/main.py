from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.timing import add_timing_middleware
from contextlib import asynccontextmanager

from app.core.dependencies import get_app_settings, get_keep_alive
from app.utils.logging import logger, configure_logging, LOGGING_CONFIG

from app.api.v1.transcription_router import router as transcription_router
from app.api.v1.codetotext_router import router as codetotext_router
from app.api.v1.getanswer_router import router as getanswer_router
from app.middleware.logging import add_request_id


configure_logging()
settings = get_app_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    keep_alive = get_keep_alive()
    task = await keep_alive.start()
    try:
        yield
    finally:
        await keep_alive.stop(task)


app = FastAPI(
    title=settings.project.name,
    lifespan=lifespan,
)

app.middleware("http")(add_request_id)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.project.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_timing_middleware(
    app,
    record=logger.info,
    prefix="request"
)


app.include_router(
    transcription_router,
    prefix="/transcribe",
    tags=["transcription"],
)
app.include_router(
    codetotext_router,
    prefix="/codetotext",
    tags=["code to text"],
)
app.include_router(
    getanswer_router,
    prefix="/getanswer",
    tags=["get answer"],
)


def run():
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.project.host,
        port=settings.project.port,
        reload=settings.project.debug,
        log_level="debug",
        log_config=LOGGING_CONFIG,
    )


if __name__ == "__main__":
    run()
