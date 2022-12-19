"""tqdm logs

Revision ID: 8bd8512b49d5
Revises: 02464cf704bf
Create Date: 2022-12-19 23:05:44.855762

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '8bd8512b49d5'
down_revision = '02464cf704bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tqdm_logs',
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
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('current', sa.Integer(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=True),
        sa.Column('need_time', sa.String(), nullable=False),
        sa.Column('need_time_for_all', sa.String(), nullable=False),
        sa.Column('avg_data', sa.String(), nullable=False),
        sa.Column('all_time', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__tqdm_logs')),
        sa.UniqueConstraint('id', name=op.f('uq__tqdm_logs__id')),
        sa.UniqueConstraint('name', name=op.f('uq__tqdm_logs__name')),
    )


def downgrade() -> None:
    op.drop_table('tqdm_logs')
