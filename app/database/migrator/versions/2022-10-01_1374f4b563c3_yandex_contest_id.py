"""add yandex_contest_id in contest and refactoring

Revision ID: 1374f4b563c3
Revises: eab58e734f0c
Create Date: 2022-10-01 13:24:28.777655

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '1374f4b563c3'
down_revision = 'eab58e734f0c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'contest', sa.Column('yandex_contest_id', sa.Integer(), nullable=True)
    )
    op.execute(
        "UPDATE contest SET yandex_contest_id = REVERSE(SPLIT_PART(REVERSE(link), '/', 1))::int"
    )
    op.alter_column('contest', 'yandex_contest_id', nullable=False)
    op.create_index(
        op.f('ix__contest__yandex_contest_id'),
        'contest',
        ['yandex_contest_id'],
        unique=True,
    )

    op.create_unique_constraint(op.f('uq__contest__id'), 'contest', ['id'])
    op.create_unique_constraint(op.f('uq__contest__link'), 'contest', ['link'])
    op.create_unique_constraint(op.f('uq__course__id'), 'course', ['id'])
    op.create_unique_constraint(
        op.f('uq__department__id'), 'department', ['id']
    )
    op.create_index(
        op.f('ix__student__contest_login'),
        'student',
        ['contest_login'],
        unique=True,
    )
    op.create_unique_constraint(op.f('uq__student__id'), 'student', ['id'])
    op.create_unique_constraint(
        op.f('uq__student__token'), 'student', ['token']
    )
    op.create_unique_constraint(
        op.f('uq__student_contest__id'), 'student_contest', ['id']
    )
    op.create_unique_constraint(
        op.f('uq__student_course__id'), 'student_course', ['id']
    )
    op.create_unique_constraint(
        op.f('uq__student_department__id'), 'student_department', ['id']
    )
    op.create_unique_constraint(op.f('uq__user__id'), 'user', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint(op.f('uq__user__id'), 'user', type_='unique')
    op.drop_constraint(
        op.f('uq__student_department__id'),
        'student_department',
        type_='unique',
    )
    op.drop_constraint(
        op.f('uq__student_course__id'), 'student_course', type_='unique'
    )
    op.drop_constraint(
        op.f('uq__student_contest__id'), 'student_contest', type_='unique'
    )
    op.drop_constraint(op.f('uq__student__token'), 'student', type_='unique')
    op.drop_constraint(op.f('uq__student__id'), 'student', type_='unique')
    op.drop_index(op.f('ix__student__contest_login'), table_name='student')
    op.drop_constraint(
        op.f('uq__department__id'), 'department', type_='unique'
    )
    op.drop_constraint(op.f('uq__course__id'), 'course', type_='unique')
    op.drop_constraint(op.f('uq__contest__link'), 'contest', type_='unique')
    op.drop_constraint(op.f('uq__contest__id'), 'contest', type_='unique')
    op.drop_index(op.f('ix__contest__yandex_contest_id'), table_name='contest')
    op.drop_column('contest', 'yandex_contest_id')
