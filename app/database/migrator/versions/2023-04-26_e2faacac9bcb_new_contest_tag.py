"""new contest tag

Revision ID: e2faacac9bcb
Revises: 9e5965fa461b
Create Date: 2023-04-26 12:38:49.042668

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e2faacac9bcb'
down_revision = '9e5965fa461b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE tag ADD VALUE 'EARLY_EXAM'")

    op.create_unique_constraint(
        op.f('uq__contest_group__id'), 'contest_group', ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__contest_group__id'), 'contest_group', type_='unique'
    )

    with op.get_context().autocommit_block():
        op.execute(
            'DELETE FROM pg_enum '
            "WHERE enumlabel = 'EARLY_EXAM' "
            'AND enumtypid = ('
            "SELECT oid FROM pg_type WHERE typname = 'tag'"
            ')'
        )
