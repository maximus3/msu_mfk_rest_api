"""author id unique

Revision ID: b5bcf29a1342
Revises: 6792d16b22be
Create Date: 2023-10-13 17:17:36.300439

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b5bcf29a1342'
down_revision = '6792d16b22be'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'student_contest',
        'author_id',
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.create_unique_constraint(
        op.f('uq__student_contest__author_id'),
        'student_contest',
        ['author_id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__student_contest__author_id'),
        'student_contest',
        type_='unique',
    )
    op.alter_column(
        'student_contest',
        'author_id',
        existing_type=sa.INTEGER(),
        nullable=True,
    )
