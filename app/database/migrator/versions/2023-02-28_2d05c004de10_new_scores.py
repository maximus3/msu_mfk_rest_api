"""new scores

Revision ID: 2d05c004de10
Revises: 34634ae740af
Create Date: 2023-02-28 15:59:09.390027

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '2d05c004de10'
down_revision = '34634ae740af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_course',
        sa.Column(
            'score_no_deadline',
            sa.Float(),
            server_default='0.0',
            nullable=False,
        ),
    )
    op.execute('UPDATE student_course SET score_no_deadline = score')
    op.drop_column('student_course', 'contests_ok_percent')
    op.drop_column('student_course', 'score_percent')
    op.add_column(
        'student_task',
        sa.Column(
            'best_score_before_finish',
            sa.Float(),
            server_default='0.0',
            nullable=False,
        ),
    )
    op.execute(
        'UPDATE student_task SET best_score_before_finish = final_score'
    )
    op.add_column(
        'student_task',
        sa.Column(
            'best_score', sa.Float(), nullable=False, server_default='0.0'
        ),
    )
    op.execute('UPDATE student_task SET best_score = no_deadline_score')
    op.add_column(
        'student_task',
        sa.Column(
            'best_score_before_finish_submission_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.execute(
        'UPDATE student_task SET best_score_before_finish_submission_id = best_submission_id'
    )
    op.add_column(
        'student_task',
        sa.Column(
            'best_score_submission_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.execute(
        'UPDATE student_task SET best_score_submission_id = best_no_deadline_submission_id'
    )
    op.drop_column('student_task', 'best_no_deadline_submission_id')
    op.drop_column('student_task', 'best_submission_id')
    op.drop_column('student_task', 'no_deadline_score')
    op.add_column(
        'submission',
        sa.Column('score', sa.Float(), server_default='0.0', nullable=False),
    )
    op.execute('UPDATE submission SET score = no_deadline_score')
    op.add_column(
        'submission',
        sa.Column(
            'score_before_finish',
            sa.Float(),
            server_default='0.0',
            nullable=False,
        ),
    )
    op.execute('UPDATE submission SET score_before_finish = final_score')
    op.drop_column('submission', 'no_deadline_score')


def downgrade() -> None:
    op.add_column(
        'submission',
        sa.Column(
            'no_deadline_score',
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.execute('UPDATE submission SET no_deadline_score = score')
    op.drop_column('submission', 'score_before_finish')
    op.drop_column('submission', 'score')
    op.add_column(
        'student_task',
        sa.Column(
            'no_deadline_score',
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.execute('UPDATE student_task SET no_deadline_score = best_score')
    op.add_column(
        'student_task',
        sa.Column(
            'best_submission_id',
            postgresql.UUID(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.execute(
        'UPDATE student_task SET best_submission_id = best_score_before_finish_submission_id'
    )
    op.add_column(
        'student_task',
        sa.Column(
            'best_no_deadline_submission_id',
            postgresql.UUID(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.execute(
        'UPDATE student_task SET best_no_deadline_submission_id = best_score_submission_id'
    )
    op.drop_column('student_task', 'best_score_submission_id')
    op.drop_column('student_task', 'best_score_before_finish_submission_id')
    op.drop_column('student_task', 'best_score')
    op.drop_column('student_task', 'best_score_before_finish')
    op.add_column(
        'student_course',
        sa.Column(
            'score_percent',
            postgresql.DOUBLE_PRECISION(precision=53),
            server_default=sa.text("'0'::double precision"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'contests_ok_percent',
            postgresql.DOUBLE_PRECISION(precision=53),
            server_default=sa.text("'0'::double precision"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column('student_course', 'score_no_deadline')
