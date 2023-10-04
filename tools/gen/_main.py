import pathlib
import typing as tp

import jinja2
from loguru import logger

from app.schemas import gen as gen_schemas


def main(*args: tp.Any, **kwargs: tp.Any) -> None:
    jinja2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            pathlib.Path(__file__).parent / 'templates'
        )
    )
    template = jinja2_env.get_template('_list_of_gens.py.jinja2')
    _gen(
        gen_name='_list_of_gens',
        dir_for_create=pathlib.Path(__file__).parent,
        data_for_gens={
            '_list_of_gens': gen_schemas.DataForGen(
                template=template,
                recreate=True,
                gen_kwargs={
                    'gen_modules': list(
                        map(
                            lambda x: x.stem,
                            pathlib.Path('./tools/gen').glob('gen_*.py'),
                        )
                    )
                },
            )
        },
    )

    from ._list_of_gens import (  # pylint: disable=import-outside-toplevel
        list_of_gens,
    )

    for gen_dict in list_of_gens:
        _gen(
            gen_dict['name'],  # type: ignore
            *gen_dict['func'](  # type: ignore
                jinja2_env=gen_dict['jinja2_env'], *args, **kwargs
            ),
        )


def _gen(
    gen_name: str,
    dir_for_create: pathlib.Path,
    data_for_gens: dict[str, gen_schemas.DataForGen],
) -> None:
    if not data_for_gens:
        logger.info('No data for gen, skipping {}', gen_name)
        return
    dir_for_create.mkdir(exist_ok=True)
    already_exists = {path.stem for path in dir_for_create.iterdir()}
    for name, data_for_gen in data_for_gens.items():
        if name in already_exists and not data_for_gen.recreate:
            logger.info('Skipping {} because it already exists.', name)
            continue
        data_for_gen.gen_dir = data_for_gen.gen_dir or dir_for_create

        with open(
            data_for_gen.gen_dir / f'{name}.py',
            'w',
            encoding='utf-8',
        ) as f:
            f.write(
                data_for_gen.template.render(
                    **data_for_gen.gen_kwargs,
                )
            )
        logger.info('Generated {} for {}.', name, gen_name)
