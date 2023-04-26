"""add usual tags

Revision ID: d70f50627143
Revises: e2faacac9bcb
Create Date: 2023-04-26 13:43:46.635905

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd70f50627143'
down_revision = 'e2faacac9bcb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE tag ADD VALUE 'USUAL'")
        op.execute("ALTER TYPE grouptag ADD VALUE 'USUAL'")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            'DELETE FROM pg_enum '
            "WHERE enumlabel = 'USUAL' "
            'AND enumtypid = ('
            "SELECT oid FROM pg_type WHERE typname = 'tag'"
            ')'
        )
        op.execute(
            'DELETE FROM pg_enum '
            "WHERE enumlabel = 'USUAL' "
            'AND enumtypid = ('
            "SELECT oid FROM pg_type WHERE typname = 'grouptag'"
            ')'
        )
