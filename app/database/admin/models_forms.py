import typing as tp

from wtforms import SelectField

from app.database.admin import mappings
from app.database.connection import SessionManager


def get_form_overrides(models_names: list[str]) -> dict[str, SelectField]:
    return {
        model_name.lower() + '_id': SelectField for model_name in models_names
    }


def get_form_args(
    models_names: list[str],
) -> dict[str, dict[str, tp.Any]]:
    data = {}
    for model_name in models_names:
        filter_model = Filter(model_name)
        data[model_name.lower() + '_id'] = {
            'choices': IterNamesMapper(model_name),
            'filters': [filter_model],
            'validate_choice': False,
        }
    return data


class IterNamesMapper:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._data: list[str] | None = None

    def __iter__(self):  # type: ignore
        self._data = list(get_mapper(self.model_name).keys())[::-1]
        return self

    def __next__(self):  # type: ignore
        if self._data is None:
            raise StopIteration
        if not self._data:
            self._data = None
            raise StopIteration
        return self._data.pop()


class Filter:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._data = None

    def __call__(self, x: str | None) -> tp.Any:
        mapping = get_mapper(self.model_name)
        if x is None:
            return None
        if x not in mapping:
            raise ValueError(f'Unknown value {x} {self.model_name}')
        return mapping[x]


def get_mapper(model_name: str) -> dict[str, tp.Any]:
    with SessionManager().create_session() as session:
        return {
            elem.real_repr(session)
            if hasattr(elem, 'real_repr')
            else repr(elem): elem.id
            for elem in session.query(
                mappings.tablename_to_model[model_name]
            ).all()
        }
