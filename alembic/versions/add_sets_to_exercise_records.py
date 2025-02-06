"""add sets to exercise records

Revision ID: add_sets_to_exercise_records
Revises: add_updated_at_to_pt_sessions
Create Date: 2024-03-19 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_sets_to_exercise_records'
down_revision: Union[str, None] = 'add_updated_at_to_pt_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. sets 컬럼 추가
    op.add_column('exercise_records',
        sa.Column('sets', sa.Integer(), nullable=True, default=1)
    )
    
    # 2. 기존 레코드의 sets를 1로 설정
    op.execute("""
        UPDATE exercise_records 
        SET sets = 1 
        WHERE sets IS NULL
    """)
    
    # 3. NOT NULL 제약조건 추가
    op.alter_column('exercise_records', 'sets',
        existing_type=sa.Integer(),
        nullable=False
    )

def downgrade() -> None:
    # sets 컬럼 삭제
    op.drop_column('exercise_records', 'sets') 