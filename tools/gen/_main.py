import pathlib
import typing as tp

import jinja2
from loguru import logger

from .gen_admin_models import main as gen_admin_models
from .gen_schedulers import make_data as make_data_gen_schedulers


def main(*args: tp.Any, **kwargs: tp.Any) -> None:
    # gen_admin_models
    jinja2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            pathlib.Path(__file__).parent / 'gen_admin_models' / 'templates'
        )
    )
    gen_admin_models(jinja2_env=jinja2_env, *args, **kwargs)

    # gen_schedulers
    jinja2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            pathlib.Path(__file__).parent / 'gen_schedulers' / 'templates'
        )
    )
    dir_for_create, data_for_gen = make_data_gen_schedulers(
        jinja2_env=jinja2_env, *args, **kwargs
    )
    _gen('gen_schedulers', dir_for_create, data_for_gen)


def _gen(
    gen_name: str,
    dir_for_create: pathlib.Path,
    data_for_gen: dict[str, tuple[jinja2.Template, bool, dict[str, tp.Any]]],
) -> None:
    if not data_for_gen:
        logger.info('No data for gen, skipping {}', gen_name)
        return
    dir_for_create.mkdir(exist_ok=True)
    already_exists = {path.stem for path in dir_for_create.iterdir()}
    for name, (template, recreate, gen_kwargs) in data_for_gen.items():
        if name in already_exists and not recreate:
            logger.info('Skipping {} because it already exists.', name)
            continue

        with open(
            dir_for_create / f'{name}.py',
            'w',
            encoding='utf-8',
        ) as f:
            f.write(
                template.render(
                    **gen_kwargs,
                )
            )
        logger.info('Generated {}.', name)
