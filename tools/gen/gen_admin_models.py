# pylint: disable=too-many-statements

from loguru import logger
import pathlib

import jinja2

from app.config import get_settings
from app.database import models


def main(
    jinja2_env: jinja2.Environment, recreate_str: str = 'recreate'
) -> None:
    """Generate models for sqladmin."""

    recreate = recreate_str.lower() == 'recreate'

    settings = get_settings()
    template = jinja2_env.get_template('admin_model.py.jinja2')
    init_template = jinja2_env.get_template('__init__.py.jinja2')
    mappings_template = jinja2_env.get_template('mappings.py.jinja2')

    admin_models_dir = (
        pathlib.Path(settings.BASE_DIR)
        / 'app'
        / 'database'
        / 'admin'
        / 'models'
    )
    admin_models_dir.mkdir(exist_ok=True)
    already_exists = {path.stem for path in admin_models_dir.iterdir()}

    db_models = {
        model.__tablename__: model
        for model in models.BaseModel.__subclasses__()
    }
    logger.info('Found {} models in database.', len(db_models))
    for model in db_models.values():
        if model.__tablename__ in already_exists and not recreate:
            logger.info(
                'Skipping {} because it already exists.', model.__tablename__
            )
            continue
        with open(
            admin_models_dir / f'{model.__tablename__}.py',
            'w',
            encoding='utf-8',
        ) as f:
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

            f.write(
                template.render(
                    model=model,
                    column_list=column_list,
                    form_excluded_columns=form_excluded_columns,
                    foreign_keys=foreign_keys,
                )
            )
        logger.info('Generated {}.', model.__tablename__)

    with open(admin_models_dir / '__init__.py', 'w', encoding='utf-8') as f:
        f.write(
            init_template.render(
                models=sorted(
                    db_models.values(), key=lambda m: m.__tablename__
                )
            )
        )
    logger.info('Generated __init__.py.')

    with open(
        admin_models_dir.parent / 'mappings.py', 'w', encoding='utf-8'
    ) as f:
        f.write(
            mappings_template.render(
                models=sorted(
                    db_models.values(), key=lambda m: m.__tablename__
                )
            )
        )
    logger.info('Generated mappings.py.')
