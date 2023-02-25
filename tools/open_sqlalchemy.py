import typing as tp

from app.database.connection import SessionManager


def main(*_: tp.Any) -> None:
    """Open sqlalchemy session."""

    SessionManager().refresh()
    with SessionManager().create_session() as session:  # noqa: F841  # pylint: disable=unused-variable
        breakpoint()  # pylint: disable=forgotten-debug-statement
