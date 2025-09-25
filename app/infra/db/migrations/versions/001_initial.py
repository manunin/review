"""Initial migration - create tasks table

Revision ID: 001_initial
Revises: 
Create Date: 2025-09-15 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('start', sa.Integer(), nullable=True),
        sa.Column('end', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('sentiment', sa.String(length=10), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('total_reviews', sa.Integer(), nullable=True),
        sa.Column('positive', sa.Integer(), nullable=True),
        sa.Column('negative', sa.Integer(), nullable=True),
        sa.Column('neutral', sa.Integer(), nullable=True),
        sa.Column('positive_percentage', sa.Float(), nullable=True),
        sa.Column('negative_percentage', sa.Float(), nullable=True),
        sa.Column('neutral_percentage', sa.Float(), nullable=True),
        sa.Column('error_code', sa.String(length=2), nullable=True),
        sa.Column('error_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)
    op.create_index('ix_tasks_task_id', 'tasks', ['task_id'], unique=True)
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('ix_tasks_type', 'tasks', ['type'], unique=False)
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tasks_created_at', table_name='tasks')
    op.drop_index('ix_tasks_type', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_index('ix_tasks_task_id', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    
    # Drop table
    op.drop_table('tasks')
