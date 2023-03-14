# pylint: disable=too-many-statements,duplicate-code

import pathlib
import typing as tp

import jinja2
import loguru

from app.config import get_settings
from app.database import models
from app.schemas import gen as gen_schemas


TYPE_TO_FUZZY = {
    'UUID': 'Faker(\'uuid4\')',
    'TIMESTAMP': 'Faker(\'date_time\')',
    'INTEGER': 'fuzzy.FuzzyInteger(1, 10000)',
    'DATETIME': 'Faker(\'date_time\')',
    'VARCHAR': 'fuzzy.FuzzyText()',
    'FLOAT': 'fuzzy.FuzzyFloat(0, 1)',
    'BOOLEAN': 'fuzzy.FuzzyChoice([True, False])',
    'TEXT': 'fuzzy.FuzzyText(length=64)',
    'ARRAY': '[]  # type: ignore',
    'JSON': '\'{}\'',
}


def make_data(
    jinja2_env: jinja2.Environment,
    *_: tp.Any,
    **__: tp.Any,
) -> tuple[pathlib.Path, dict[str, gen_schemas.DataForGen]]:
    """Generate models for factory lib (tests)."""

    settings = get_settings()
    template = jinja2_env.get_template('factory_model.py.jinja2')
    init_template = jinja2_env.get_template('__init__.py.jinja2')

    dir_for_create = pathlib.Path(settings.BASE_DIR) / 'tests' / 'factory_lib'

    db_models = sorted(
        models.BaseModel.__subclasses__(), key=lambda m: m.__tablename__
    )

    data_for_gen = {
        '__init__': gen_schemas.DataForGen(
            template=init_template,
            recreate=True,
            gen_kwargs={'models': db_models},
        ),
    }
    for model in db_models:
        form_excluded_columns = ['id', 'dt_created', 'dt_updated']
        columns_with_types = {}
        for column in model.__table__.columns:
            if column.name in form_excluded_columns:
                continue
            column_type = str(column.type)
            if column_type.startswith('VARCHAR'):
                column_type = 'VARCHAR'
            if column_type not in TYPE_TO_FUZZY:
                loguru.logger.warning('No type for {}', str(column.type))
                continue
            columns_with_types[column.name] = TYPE_TO_FUZZY[column_type]

        data_for_gen[model.__tablename__] = gen_schemas.DataForGen(
            template=template,
            recreate=True,
            gen_kwargs={
                'model': model,
                'columns_with_types': columns_with_types,
            },
        )

    return dir_for_create, data_for_gen
