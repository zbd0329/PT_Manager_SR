"""create body measurements table

Revision ID: create_body_measurements
Revises: 
Create Date: 2024-02-11 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_body_measurements'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 테이블 생성
    op.create_table(
        'body_measurements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('member_id', sa.String(36), sa.ForeignKey('members.id'), nullable=False),
        sa.Column('height', sa.Float, nullable=False),
        sa.Column('weight', sa.Float, nullable=False),
        sa.Column('body_fat', sa.Float, nullable=False),
        sa.Column('body_fat_percentage', sa.Float, nullable=False),
        sa.Column('muscle_mass', sa.Float, nullable=False),
        sa.Column('bmi', sa.Float, nullable=False),
        sa.Column('measurement_date', sa.Date, nullable=False)
    )

def downgrade():
    op.drop_table('body_measurements') 