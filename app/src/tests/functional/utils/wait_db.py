import logging

from .backoff import backoff

logger = logging.getLogger(__name__)


@backoff()
def wait_db(db, message):
    if db.ping():
        logger.info(message)
