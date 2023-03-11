# Code generated automatically.

import pathlib

import jinja2

from .gen_admin_models import make_data as gen_admin_models
from .gen_schedulers import make_data as gen_schedulers


list_of_gens = [
    {
        'name': 'gen_admin_models',
        'func': gen_admin_models,
        'jinja2_env': jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                pathlib.Path(__file__).parent
                / 'gen_admin_models'
                / 'templates'
            )
        ),
    },
    {
        'name': 'gen_schedulers',
        'func': gen_schedulers,
        'jinja2_env': jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                pathlib.Path(__file__).parent / 'gen_schedulers' / 'templates'
            )
        ),
    },
]
