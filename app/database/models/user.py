import sqlalchemy as sa

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    username = sa.Column(
        'username',
        sa.String,
        nullable=False,
        unique=True,
        index=True,
        doc='Username for authentication.',
    )
    password = sa.Column(
        'password',
        sa.String,
        nullable=False,
        index=True,
        doc='Hashed password.',
    )
