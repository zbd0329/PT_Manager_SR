"""Add exercise records table and relationships

Revision ID: e2322d677647
Revises: 612e1eb6df94
Create Date: 2024-03-19 15:23:45.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2322d677647'
down_revision: Union[str, None] = '612e1eb6df94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 기존 테이블 삭제
    op.execute("DROP TABLE IF EXISTS exercise_records")

    # 2. gender 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE members MODIFY gender VARCHAR(10)")
    
    # 3. gender 값 업데이트
    op.execute("UPDATE members SET gender = 'MALE' WHERE gender = 'M'")
    op.execute("UPDATE members SET gender = 'FEMALE' WHERE gender = 'F'")

    # 4. 새로운 enum 타입으로 변경
    op.execute("ALTER TABLE members MODIFY gender ENUM('MALE', 'FEMALE') NULL")

    # 5. trainer_id nullable 변경 및 외래 키 재설정
    op.drop_constraint('pt_sessions_ibfk_2', 'pt_sessions', type_='foreignkey')
    op.alter_column('pt_sessions', 'trainer_id',
                    existing_type=sa.String(length=36),
                    nullable=True)
    op.create_foreign_key(None, 'pt_sessions', 'users', ['trainer_id'], ['id'], ondelete='SET NULL')

    # 6. exercise_records 테이블 생성
    op.create_table('exercise_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('exercise_name', sa.String(length=100), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('repetitions', sa.Integer(), nullable=False),
        sa.Column('body_part', sa.Text(), nullable=False),
        sa.Column('input_source', sa.Enum('MEMBER', 'TRAINER', name='inputsource'), nullable=False),
        sa.Column('member_id', sa.String(length=36), nullable=False),
        sa.Column('trainer_id', sa.String(length=36), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['pt_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trainer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # 1. exercise_records 테이블 삭제
    op.drop_table('exercise_records')

    # 2. trainer_id 외래 키 및 nullable 복원
    op.drop_constraint(None, 'pt_sessions', type_='foreignkey')
    op.alter_column('pt_sessions', 'trainer_id',
                    existing_type=sa.String(length=36),
                    nullable=False)
    op.create_foreign_key('pt_sessions_ibfk_2', 'pt_sessions', 'users', ['trainer_id'], ['id'], ondelete='CASCADE')

    # 3. gender 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE members MODIFY gender VARCHAR(10)")

    # 4. gender 값 복원
    op.execute("UPDATE members SET gender = 'M' WHERE gender = 'MALE'")
    op.execute("UPDATE members SET gender = 'F' WHERE gender = 'FEMALE'")

    # 5. 원래의 enum 타입으로 복원
    op.execute("ALTER TABLE members MODIFY gender ENUM('M', 'F') NOT NULL")
