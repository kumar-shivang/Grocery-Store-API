import logging

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.ERROR)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

