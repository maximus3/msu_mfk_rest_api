"""score float

Revision ID: 629a4d968a13
Revises: b2649c8cd243
Create Date: 2022-12-15 15:27:22.068557

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '629a4d968a13'
down_revision = 'b2649c8cd243'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'student_course', 'score', existing_type=sa.INTEGER(), type_=sa.FLOAT()
    )


def downgrade() -> None:
    op.alter_column(
        'student_course', 'score', existing_type=sa.FLOAT(), type_=sa.INTEGER()
    )
