# pylint: disable=too-many-statements

import pathlib
import typing as tp

import jinja2
from loguru import logger

import tools.load_config
from app.config import get_settings
from app.schemas import gen as gen_schemas


def make_data(
    jinja2_env: jinja2.Environment, *_: tp.Any, **__: tp.Any
) -> tuple[pathlib.Path, dict[str, gen_schemas.DataForGen]]:
    """Generate workers."""

    settings = get_settings()
    init_template = jinja2_env.get_template('__init__.py.jinja2')

    dir_for_create = pathlib.Path(settings.BASE_DIR) / 'app' / 'worker'

    workers_config = tools.load_config.get_config(
        settings.BASE_DIR / settings.CONFIG_FILENAME
    ).get('worker')
    if not workers_config:
        logger.info('No workers')
        return dir_for_create, {}
    logger.info('Found {} workers in config.', len(workers_config))

    data_for_gen = {
        '__init__': gen_schemas.DataForGen(
            template=init_template,
            recreate=True,
            gen_kwargs={'tasks': workers_config},
        ),
    }

    return dir_for_create, data_for_gen
