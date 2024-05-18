"""remove levels from contests

Revision ID: 4cdd1ef9a07e
Revises: 511f95ef13de
Create Date: 2023-03-14 18:19:11.429868

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '4cdd1ef9a07e'
down_revision = '511f95ef13de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('contest', 'levels')


def downgrade() -> None:
    op.add_column(
        'contest',
        sa.Column(
            'levels',
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
