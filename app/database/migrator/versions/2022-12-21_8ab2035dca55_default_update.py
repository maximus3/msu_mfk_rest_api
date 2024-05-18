"""default update

Revision ID: 8ab2035dca55
Revises: 3632ceef0d48
Create Date: 2022-12-21 20:37:15.938579

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '8ab2035dca55'
down_revision = '3632ceef0d48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'default_update_on',
            sa.Boolean(),
            server_default='true',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('course', 'default_update_on')
