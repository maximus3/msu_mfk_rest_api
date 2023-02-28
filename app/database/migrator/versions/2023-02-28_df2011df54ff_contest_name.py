"""contest name

Revision ID: df2011df54ff
Revises: 2d05c004de10
Create Date: 2023-02-28 16:21:19.952521

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'df2011df54ff'
down_revision = '2d05c004de10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'contest',
        sa.Column(
            'name_format',
            sa.String(),
            server_default='Лекция {lecture_num}',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('contest', 'name_format')
