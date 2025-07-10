from alembic import op
import sqlalchemy as sa

revision = '0005_add_exercises'
down_revision = '0004_add_workout_time'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metric_type', sa.String(), nullable=False),
    )
    op.add_column('sets', sa.Column('exercise_id', sa.Integer(), sa.ForeignKey('exercises.id'), nullable=True))
    op.drop_column('sets', 'exercise')


def downgrade():
    op.add_column('sets', sa.Column('exercise', sa.String(), nullable=True))
    op.drop_column('sets', 'exercise_id')
    op.drop_table('exercises')
