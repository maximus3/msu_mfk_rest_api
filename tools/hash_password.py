from loguru import logger

from app.utils.common import hash_password


def main(password: str) -> None:
    logger.info('Hash for {} is {}', password, hash_password(password))
