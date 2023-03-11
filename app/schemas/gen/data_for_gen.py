import pathlib
import typing as tp

import jinja2
from pydantic import BaseModel


class DataForGen(BaseModel):
    template: jinja2.Template
    recreate: bool
    gen_kwargs: dict[str, tp.Any]
    gen_dir: pathlib.Path | None = None

    class Config:
        arbitrary_types_allowed = True
