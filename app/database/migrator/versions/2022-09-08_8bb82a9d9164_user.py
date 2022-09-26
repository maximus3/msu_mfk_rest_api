"""empty message

Revision ID: 8bb82a9d9164
Revises:
Create Date: 2022-09-08 22:30:55.851803

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '8bb82a9d9164'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('username', sa.TEXT(), nullable=False),
        sa.Column('password', sa.TEXT(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__user')),
        sa.UniqueConstraint('id', name=op.f('uq__user__id')),
    )
    op.create_index(
        op.f('ix__user__password'), 'user', ['password'], unique=False
    )
    op.create_index(
        op.f('ix__user__username'), 'user', ['username'], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f('ix__user__username'), table_name='user')
    op.drop_index(op.f('ix__user__password'), table_name='user')
    op.drop_table('user')