"""group tag

Revision ID: 1b8f78168337
Revises: ee32f6a3e6a6
Create Date: 2023-04-26 11:48:53.674347

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '1b8f78168337'
down_revision = 'ee32f6a3e6a6'
branch_labels = None
depends_on = None

types = [
    sa.Enum('EARLY_EXAM', name='grouptag'),
]


def upgrade() -> None:
    for type_ in types:
        type_.create(op.get_bind(), checkfirst=False)

    op.add_column(
        'group',
        sa.Column(
            'tags',
            sa.ARRAY(sa.Enum('EARLY_EXAM', name='grouptag')),
            server_default='{}',
            nullable=False,
        ),
    )
    op.create_unique_constraint(op.f('uq__group__id'), 'group', ['id'])
    op.create_unique_constraint(
        op.f('uq__student_group__id'), 'student_group', ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__student_group__id'), 'student_group', type_='unique'
    )
    op.drop_constraint(op.f('uq__group__id'), 'group', type_='unique')
    op.drop_column('group', 'tags')

    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)
