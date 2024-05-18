"""contest_group relation

Revision ID: 9e5965fa461b
Revises: 1b8f78168337
Create Date: 2023-04-26 12:26:59.736798

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '9e5965fa461b'
down_revision = '1b8f78168337'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'contest_group',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contest_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__contest_group__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['group.id'],
            name=op.f('fk__contest_group__group_id__group'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__contest_group')),
        sa.UniqueConstraint('id', name=op.f('uq__contest_group__id')),
    )
    op.create_index(
        op.f('ix__contest_group__contest_id'),
        'contest_group',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__contest_group__group_id'),
        'contest_group',
        ['group_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix__contest_group__group_id'), table_name='contest_group'
    )
    op.drop_index(
        op.f('ix__contest_group__contest_id'), table_name='contest_group'
    )
    op.drop_table('contest_group')
