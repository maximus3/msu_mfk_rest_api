"""course contest_count

Revision ID: 2569e4e1fdf6
Revises: 3025eda76ca5
Create Date: 2023-02-23 12:57:33.273135

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '2569e4e1fdf6'
down_revision = '3025eda76ca5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'contest_count', sa.Integer(), server_default='0', nullable=False
        ),
    )
    op.create_unique_constraint(
        op.f('uq__submission__id'), 'submission', ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__submission__id'), 'submission', type_='unique'
    )
    op.drop_column('course', 'contest_count')
