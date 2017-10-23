import asyncio
import importlib
import os

settings = importlib.import_module(os.getenv('SETTINGS_MODULE', 'tachikoma.settings'))

loop = asyncio.get_event_loop()
loop.set_debug(True)

import structlog
import logging

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