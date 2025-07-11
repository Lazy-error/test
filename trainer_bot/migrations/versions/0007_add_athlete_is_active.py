from alembic import op
import sqlalchemy as sa

revision = '0007_add_athlete_is_active'
down_revision = '0006_add_user_timezone'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('athletes', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column('athletes', 'is_active', server_default=None)

def downgrade():
    op.drop_column('athletes', 'is_active')
