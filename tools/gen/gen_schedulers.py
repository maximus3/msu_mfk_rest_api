# pylint: disable=too-many-statements

import logging
import pathlib
import typing as tp

import jinja2

import tools.load_config
from app.config import get_settings


def make_data(
    jinja2_env: jinja2.Environment, *_: tp.Any, **__: tp.Any
) -> tuple[
    pathlib.Path, dict[str, tuple[jinja2.Template, bool, dict[str, tp.Any]]]
]:
    """Generate schedulers."""

    logger = logging.getLogger(__name__)

    settings = get_settings()
    init_template = jinja2_env.get_template('__init__.py.jinja2')
    main_template = jinja2_env.get_template('__main__.py.jinja2')
    job_template = jinja2_env.get_template('job.py.jinja2')

    dir_for_create = pathlib.Path(settings.BASE_DIR) / 'app' / 'scheduler'

    schedulers_config = tools.load_config.get_config(
        settings.BASE_DIR / settings.CONFIG_FILENAME
    ).get('scheduler')
    if not schedulers_config:
        logger.info('No schedulers')
        return dir_for_create, {}
    logger.info('Found {} schedulers in config.', len(schedulers_config))

    data_for_gen = {
        '__init__': (init_template, True, {'jobs': schedulers_config}),
        '__main__': (main_template, True, {}),
    }
    for job_name in schedulers_config:
        data_for_gen[job_name] = (job_template, False, {})

    return dir_for_create, data_for_gen
