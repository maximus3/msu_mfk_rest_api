from os import environ

from .default import DefaultSettings
from .production import ProductionSettings


def get_settings() -> DefaultSettings:  # pragma: no cover
    env = environ.get('ENV', 'local')
    if env == 'local':
        return DefaultSettings()
    if env == 'production':
        return ProductionSettings()
    # ...
    # space for other settings
    # ...
    return DefaultSettings()  # fallback to default
