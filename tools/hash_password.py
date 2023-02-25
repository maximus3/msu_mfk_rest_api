import logging

from app.utils.common import hash_password


def main(password: str) -> None:
    logger = logging.getLogger(__name__)
    logger.info('Hash for %s is %s', password, hash_password(password))
