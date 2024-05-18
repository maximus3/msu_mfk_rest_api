"""add chat assistant allowed flag

Revision ID: 6792d16b22be
Revises: 938311ab5fcb
Create Date: 2023-09-27 13:56:20.139941

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '6792d16b22be'
down_revision = '938311ab5fcb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'is_smart_suggests_allowed',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('course', 'is_smart_suggests_allowed')
