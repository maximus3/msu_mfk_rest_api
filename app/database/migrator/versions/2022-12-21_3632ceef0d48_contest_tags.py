"""contest tags

Revision ID: 3632ceef0d48
Revises: 8bd8512b49d5
Create Date: 2022-12-21 18:41:23.022950

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '3632ceef0d48'
down_revision = '8bd8512b49d5'
branch_labels = None
depends_on = None

types = [
    sa.Enum('NECESSARY', 'FINAL', name='tag'),
]


def upgrade() -> None:
    for type_ in types:
        type_.create(op.get_bind(), checkfirst=False)

    op.add_column(
        'contest',
        sa.Column(
            'tags',
            sa.ARRAY(sa.Enum('NECESSARY', 'FINAL', name='tag')),
            nullable=False,
            server_default='{}',
        ),
    )
    op.execute(
        "UPDATE contest SET tags = array_append(tags, 'NECESSARY') WHERE is_necessary = TRUE"
    )
    op.drop_column('contest', 'is_necessary')
    op.create_unique_constraint(op.f('uq__tqdm_logs__id'), 'tqdm_logs', ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq__tqdm_logs__id'), 'tqdm_logs', type_='unique')
    op.add_column(
        'contest',
        sa.Column(
            'is_necessary', sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
    )
    op.execute(
        "UPDATE contest SET is_necessary = TRUE WHERE 'NECESSARY' = ANY(tags)"
    )
    op.drop_column('contest', 'tags')

    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)
