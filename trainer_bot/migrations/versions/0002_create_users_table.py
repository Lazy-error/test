from alembic import op
import sqlalchemy as sa

revision = '0002_create_users_table'
down_revision = '0001_create_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
    )


def downgrade():
    op.drop_table('users')

