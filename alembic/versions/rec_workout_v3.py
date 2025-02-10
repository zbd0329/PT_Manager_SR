"""create recommended workout tables v3

Revision ID: rec_v3
Revises: add_sets_to_exercise_records
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rec_v3'
down_revision = 'add_sets_to_exercise_records'
branch_labels = None
depends_on = None


def upgrade():
    # Create recommended_workouts table
    op.create_table(
        'recommended_workouts',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('member_id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('workout_name', sa.String(length=100), nullable=False),
        sa.Column('total_duration', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['pt_sessions.id'], ondelete='CASCADE')
    )
    
    # Create indexes for recommended_workouts
    op.create_index('idx_member_id', 'recommended_workouts', ['member_id'])
    op.create_index('idx_session_id', 'recommended_workouts', ['session_id'])

    # Create recommended_exercises table
    op.create_table(
        'recommended_exercises',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('exercise_name', sa.String(length=100), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('repetitions', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('rest_time', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['workout_id'], ['recommended_workouts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for recommended_exercises
    op.create_index('idx_workout_id', 'recommended_exercises', ['workout_id'])


def downgrade():
    op.drop_table('recommended_exercises')
    op.drop_table('recommended_workouts') 