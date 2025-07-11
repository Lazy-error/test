from alembic import op
import sqlalchemy as sa

revision = '0008_add_set_rest_sec'
down_revision = '0007_add_athlete_is_active'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sets', sa.Column('rest_sec', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('sets', 'rest_sec')
