"""add_index_status_to_documents

Revision ID: baf1b3045e48
Revises: b5774c737e30
Create Date: 2026-01-17 21:11:38.647652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'baf1b3045e48'
down_revision = 'b5774c737e30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add index_status and index_error columns to documents table
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE indexstatus AS ENUM ('not_indexed', 'indexing', 'indexed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.add_column('documents', sa.Column('index_status', sa.Enum('not_indexed', 'indexing', 'indexed', 'failed', name='indexstatus'), nullable=False, server_default='not_indexed'))
    op.add_column('documents', sa.Column('index_error', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove index_status and index_error columns (if they exist)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE documents DROP COLUMN IF EXISTS index_error;
            ALTER TABLE documents DROP COLUMN IF EXISTS index_status;
        EXCEPTION
            WHEN undefined_column THEN null;
        END $$;
    """)
    op.execute("DROP TYPE IF EXISTS indexstatus;")
