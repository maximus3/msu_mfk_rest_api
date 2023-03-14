"""delete time from start

Revision ID: 511f95ef13de
Revises: f745be74bd97
Create Date: 2023-03-14 18:17:50.391973

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '511f95ef13de'
down_revision = 'f745be74bd97'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('submission', 'time_from_start')


def downgrade() -> None:
    op.add_column(
        'submission',
        sa.Column(
            'time_from_start',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
            server_default='0',
        ),
    )
