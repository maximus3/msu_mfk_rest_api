import sqlalchemy as sa

from .base import BaseModel


class TQDMLogs(BaseModel):
    __tablename__ = 'tqdm_logs'

    name = sa.Column(sa.String, nullable=False, unique=True)
    current = sa.Column(sa.Integer, nullable=False)
    total = sa.Column(sa.Integer, nullable=True)
    need_time = sa.Column(sa.String, nullable=False)
    need_time_for_all = sa.Column(sa.String, nullable=False)
    avg_data = sa.Column(sa.String, nullable=False)
    all_time = sa.Column(sa.String, nullable=False)

    def __repr__(self):  # type: ignore
        return f'<TQDMLogs {self.name}>'
