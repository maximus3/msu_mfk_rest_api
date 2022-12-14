"""not null score

Revision ID: 1f477bbfbc3e
Revises: 22c6121b977b
Create Date: 2022-12-14 19:54:50.063699

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '1f477bbfbc3e'
down_revision = '22c6121b977b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        'UPDATE student_contest SET tasks_done = 0 WHERE tasks_done IS NULL'
    )
    op.alter_column(
        'student_contest',
        'tasks_done',
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.execute('UPDATE student_contest SET score = 0.0 WHERE score IS NULL')
    op.alter_column(
        'student_contest',
        'score',
        existing_type=postgresql.DOUBLE_PRECISION(precision=53),
        nullable=False,
    )
    op.execute('UPDATE student_contest SET is_ok = FALSE WHERE is_ok IS NULL')
    op.alter_column(
        'student_contest', 'is_ok', existing_type=sa.BOOLEAN(), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'student_contest', 'is_ok', existing_type=sa.BOOLEAN(), nullable=True
    )
    op.alter_column(
        'student_contest',
        'score',
        existing_type=postgresql.DOUBLE_PRECISION(precision=53),
        nullable=True,
    )
    op.alter_column(
        'student_contest',
        'tasks_done',
        existing_type=sa.INTEGER(),
        nullable=True,
    )
