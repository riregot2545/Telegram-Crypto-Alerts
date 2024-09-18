import logging
from logging.handlers import TimedRotatingFileHandler

from .config import USE_DOCKER
from .utils import get_logfile

formatter = logging.Formatter('%(asctime)s [%(threadName)14s] %(levelname)8s %(filename)s --> %(message)s')

# Get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get logfile name & setup file handler

if not USE_DOCKER:
    file_handler = TimedRotatingFileHandler(get_logfile(), when="d", interval=1, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    # Add handlers
    logger.addHandler(file_handler)

# Setup stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

logger.addHandler(stream_handler)
