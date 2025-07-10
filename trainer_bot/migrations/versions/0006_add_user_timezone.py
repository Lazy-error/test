from alembic import op
import sqlalchemy as sa

revision = '0006_add_user_timezone'
down_revision = '0005_add_exercises'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('timezone', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'timezone')
