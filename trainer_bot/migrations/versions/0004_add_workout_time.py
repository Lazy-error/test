from alembic import op
import sqlalchemy as sa

revision = '0004_add_workout_time'
down_revision = '0003_add_contraindications'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('workouts', sa.Column('time', sa.Time(), nullable=True))


def downgrade():
    op.drop_column('workouts', 'time')
