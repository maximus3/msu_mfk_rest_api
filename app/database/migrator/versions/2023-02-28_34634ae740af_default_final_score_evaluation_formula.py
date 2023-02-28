"""default_final_score_evaluation_formula

Revision ID: 34634ae740af
Revises: 127ae7ddff93
Create Date: 2023-02-28 15:37:14.530028

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '34634ae740af'
down_revision = '127ae7ddff93'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'contest',
        sa.Column(
            'default_final_score_evaluation_formula',
            sa.String(),
            server_default='{best_score_before_finish}',
            nullable=False,
        ),
    )
    op.add_column(
        'course',
        sa.Column(
            'default_final_score_evaluation_formula',
            sa.String(),
            server_default='{best_score_before_finish}',
            nullable=False,
        ),
    )
    op.add_column(
        'task',
        sa.Column(
            'final_score_evaluation_formula',
            sa.String(),
            server_default='{best_score_before_finish}',
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('task', 'final_score_evaluation_formula')
    op.drop_column('course', 'default_final_score_evaluation_formula')
    op.drop_column('contest', 'default_final_score_evaluation_formula')
