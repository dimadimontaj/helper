import logging, logging.config, structlog
from structlog.processors import TimeStamper
from structlog.dev import ConsoleRenderer

PRETTY = True

shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
]

renderer = ConsoleRenderer(colors=True) if PRETTY else structlog.processors.JSONRenderer()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "struct": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": renderer,
            "foreign_pre_chain": shared_processors,
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "struct",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"propagate": True},
        "uvicorn.access": {"propagate": True},
    },
}


def configure_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()






























