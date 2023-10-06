from fastapi import FastAPI
from sqladmin import Admin

from app.config import get_settings
from app.database.connection import SessionManager

from .models import model_view_list
from .security import SqlAdminAuthBackend


def get_sqladmin(app: FastAPI) -> Admin:
    SessionManager().refresh()

    admin = Admin(
        app,
        SessionManager().get_async_engine(),
        authentication_backend=SqlAdminAuthBackend(
            secret_key=get_settings().SQLADMIN_SECRET_KEY
        ),
    )

    for model_view in model_view_list:
        admin.add_view(model_view)

    return admin
