"""score no deadline

Revision ID: 02464cf704bf
Revises: 629a4d968a13
Create Date: 2022-12-19 19:07:34.641487

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '02464cf704bf'
down_revision = '629a4d968a13'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_contest',
        sa.Column(
            'score_no_deadline',
            sa.Float(),
            server_default='0.0',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('student_contest', 'score_no_deadline')
