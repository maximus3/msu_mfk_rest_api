# pylint: disable=too-many-statements

import pathlib
import typing as tp

import jinja2

from app.config import get_settings
from app.database import models
from app.schemas import gen as gen_schemas


def make_data(
    jinja2_env: jinja2.Environment,
    recreate_str: str = 'recreate',
    *_: tp.Any,
    **__: tp.Any,
) -> tuple[pathlib.Path, dict[str, gen_schemas.DataForGen]]:
    """Generate models for sqladmin."""

    recreate = recreate_str.lower() == 'recreate'

    settings = get_settings()
    template = jinja2_env.get_template('admin_model.py.jinja2')
    init_template = jinja2_env.get_template('__init__.py.jinja2')
    mappings_template = jinja2_env.get_template('mappings.py.jinja2')

    dir_for_create = (
        pathlib.Path(settings.BASE_DIR)
        / 'app'
        / 'database'
        / 'admin'
        / 'models'
    )

    db_models = sorted(
        models.BaseModel.__subclasses__(), key=lambda m: m.__tablename__
    )

    data_for_gen = {
        '__init__': gen_schemas.DataForGen(
            template=init_template,
            recreate=True,
            gen_kwargs={'models': db_models},
        ),
        'mappings': gen_schemas.DataForGen(
            template=mappings_template,
            recreate=True,
            gen_kwargs={'models': db_models},
            gen_dir=dir_for_create.parent,
        ),
    }
    for model in db_models:
        form_excluded_columns = ['id', 'dt_created', 'dt_updated']
        column_list = ['id'] + [
            f'{column.name}'
            for column in model.__table__.columns
            if column.name not in form_excluded_columns
        ]
        foreign_keys = [
            list(column.foreign_keys)[0].column.table.name
            for column in model.__table__.columns
            if column.foreign_keys
        ]

        data_for_gen[model.__tablename__] = gen_schemas.DataForGen(
            template=template,
            recreate=recreate,
            gen_kwargs={
                'model': model,
                'column_list': column_list,
                'form_excluded_columns': form_excluded_columns,
                'foreign_keys': foreign_keys,
            },
        )

    return dir_for_create, data_for_gen
