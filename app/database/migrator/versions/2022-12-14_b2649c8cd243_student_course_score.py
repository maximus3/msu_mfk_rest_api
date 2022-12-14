"""student course score

Revision ID: b2649c8cd243
Revises: 1f477bbfbc3e
Create Date: 2022-12-14 23:33:16.353217

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b2649c8cd243'
down_revision = '1f477bbfbc3e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_course',
        sa.Column('score', sa.Integer(), server_default='0', nullable=False),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'contests_ok', sa.Integer(), server_default='0', nullable=False
        ),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'score_percent', sa.Float(), server_default='0.0', nullable=False
        ),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'contests_ok_percent',
            sa.Float(),
            server_default='0.0',
            nullable=False,
        ),
    )
    op.alter_column(
        'student_course',
        'is_ok',
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text('false'),
    )


def downgrade() -> None:
    op.alter_column(
        'student_course',
        'is_ok',
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text('false'),
    )
    op.drop_column('student_course', 'contests_ok_percent')
    op.drop_column('student_course', 'score_percent')
    op.drop_column('student_course', 'contests_ok')
    op.drop_column('student_course', 'score')
