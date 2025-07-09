from alembic import op
import sqlalchemy as sa

revision = '0001_create_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'athletes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
    )
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('athlete_id', sa.Integer(), sa.ForeignKey('athletes.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_table(
        'sets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('workout_id', sa.Integer(), sa.ForeignKey('workouts.id'), nullable=False),
        sa.Column('exercise', sa.String(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
    )
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

def downgrade():
    op.drop_table('notifications')
    op.drop_table('messages')
    op.drop_table('plans')
    op.drop_table('sets')
    op.drop_table('workouts')
    op.drop_table('athletes')
