import pathlib
import typing as tp

import yaml
from loguru import logger

from app.config import get_settings


def get_config(filename: str | pathlib.Path) -> dict[tp.Any, tp.Any]:
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main(filename: str | pathlib.Path | None = None) -> None:
    filename = filename or get_settings().CONFIG_FILENAME
    logger.info('Config: {}', get_config(filename))
