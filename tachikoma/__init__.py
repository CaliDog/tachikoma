import asyncio
import importlib
import os
import structlog
import logging
import uvloop
import warnings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

try:
    settings = importlib.import_module(os.getenv('SETTINGS_MODULE', 'tachikoma.settings'))
except ImportError:
    warnings.warn("Couldn't import settings module! Perhaps you need "
                  "to create a tachikoma/settings.py file, or set your"
                  " SETTINGS_MODULE environment variable to a different"
                  "file. Proceeding with a null settings object so some"
                  " things may not work correctly.")
    settings = None

loop = asyncio.get_event_loop()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.WARNING)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

from .pipeline import Pipeline