"""add yandex id

Revision ID: 938311ab5fcb
Revises: d05766b745c2
Create Date: 2023-09-17 18:29:28.968440

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '938311ab5fcb'
down_revision = 'd05766b745c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student', sa.Column('yandex_id', sa.String(), nullable=False)
    )
    op.create_unique_constraint(
        op.f('uq__student__yandex_id'), 'student', ['yandex_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__student__yandex_id'), 'student', type_='unique'
    )
    op.drop_column('student', 'yandex_id')
