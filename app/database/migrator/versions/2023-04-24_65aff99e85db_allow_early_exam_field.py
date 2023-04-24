"""allow_early_exam field

Revision ID: 65aff99e85db
Revises: 4cdd1ef9a07e
Create Date: 2023-04-24 17:02:29.759076

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '65aff99e85db'
down_revision = '4cdd1ef9a07e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_course',
        sa.Column(
            'allow_early_exam',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('student_course', 'allow_early_exam')
