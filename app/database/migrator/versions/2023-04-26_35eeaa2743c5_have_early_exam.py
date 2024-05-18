"""have_early_exam

Revision ID: 35eeaa2743c5
Revises: 65aff99e85db
Create Date: 2023-04-26 11:06:40.046179

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '35eeaa2743c5'
down_revision = '65aff99e85db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'have_early_exam',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('course', 'have_early_exam')
