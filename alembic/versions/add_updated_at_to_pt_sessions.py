"""add updated_at to pt_sessions

Revision ID: add_updated_at_to_pt_sessions
Revises: e2322d677647
Create Date: 2024-03-19 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'add_updated_at_to_pt_sessions'
down_revision: Union[str, None] = 'e2322d677647'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. updated_at 컬럼 추가
    op.add_column('pt_sessions',
        sa.Column('updated_at', sa.DateTime, nullable=True, default=datetime.utcnow)
    )
    
    # 2. 기존 레코드의 updated_at을 created_at 값으로 설정
    op.execute("""
        UPDATE pt_sessions 
        SET updated_at = created_at 
        WHERE updated_at IS NULL
    """)
    
    # 3. NOT NULL 제약조건 추가
    op.alter_column('pt_sessions', 'updated_at',
        existing_type=sa.DateTime(),
        nullable=False
    )

def downgrade() -> None:
    # updated_at 컬럼 삭제
    op.drop_column('pt_sessions', 'updated_at') 