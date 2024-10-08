from loguru import logger
import logging
def setup_logging(logger):
    logging.getLogger().handlers = [logging.StreamHandler()]
    logger.add("file.log", rotation="10 MB")
    return logger