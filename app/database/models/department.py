import sqlalchemy as sa

from .base import BaseModel


class Department(BaseModel):
    __tablename__ = 'department'

    name = sa.Column(sa.String, unique=True)

    def __repr__(self):  # type: ignore
        return f'<Department {self.name}>'
