from structlog import get_logger

class BaseEmitter(object):
    logger = get_logger()

    def emit(self, channel, message, pipeline):
        raise NotImplementedError()

from .slack import SlackEmitter