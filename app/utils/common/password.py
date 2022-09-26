from app.config import get_settings


def hash_password(password: str) -> str:
    settings = get_settings()
    return settings.PWD_CONTEXT.hash(password)
