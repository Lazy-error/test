from alembic import op
import sqlalchemy as sa

revision = '0003_add_contraindications'
down_revision = '0002_create_users_table'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('athletes', sa.Column('contraindications', sa.String(length=250), nullable=True))


def downgrade():
    op.drop_column('athletes', 'contraindications')
