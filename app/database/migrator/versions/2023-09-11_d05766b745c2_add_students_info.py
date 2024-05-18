"""add students info

Revision ID: d05766b745c2
Revises: 2b947a6a66b9
Create Date: 2023-09-11 13:10:53.726569

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd05766b745c2'
down_revision = '2b947a6a66b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('student', sa.Column('tg_id', sa.String(), nullable=False))
    op.add_column(
        'student', sa.Column('tg_username', sa.String(), nullable=True)
    )
    op.add_column('student', sa.Column('bm_id', sa.String(), nullable=False))
    op.alter_column(
        'student', 'fio', existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        'student', 'contest_login', existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        'student', 'token', existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_index('ix__student__contest_login', table_name='student')
    op.create_unique_constraint(
        op.f('uq__student__bm_id'), 'student', ['bm_id']
    )
    op.create_unique_constraint(
        op.f('uq__student__contest_login'), 'student', ['contest_login']
    )
    op.create_unique_constraint(
        op.f('uq__student__tg_id'), 'student', ['tg_id']
    )


def downgrade() -> None:
    op.drop_constraint(op.f('uq__student__tg_id'), 'student', type_='unique')
    op.drop_constraint(
        op.f('uq__student__contest_login'), 'student', type_='unique'
    )
    op.drop_constraint(op.f('uq__student__bm_id'), 'student', type_='unique')
    op.create_index(
        'ix__student__contest_login',
        'student',
        ['contest_login'],
        unique=False,
    )
    op.alter_column(
        'student', 'token', existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        'student', 'contest_login', existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        'student', 'fio', existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column('student', 'bm_id')
    op.drop_column('student', 'tg_username')
    op.drop_column('student', 'tg_id')
