from alembic import op
import sqlalchemy as sa

revision = '0009_change_telegram_id_type'
down_revision = '0008_add_set_rest_sec'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('users', 'telegram_id', type_=sa.BigInteger())


def downgrade():
    op.alter_column('users', 'telegram_id', type_=sa.Integer())
