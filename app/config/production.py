from .default import DefaultSettings


class ProductionSettings(DefaultSettings):
    ENV: str = 'production'
    DEBUG: bool = False
