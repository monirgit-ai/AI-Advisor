"""add_heading_metadata_to_document_chunks

Revision ID: f0c6e62db04d
Revises: 5fcf03a426b8
Create Date: 2026-01-18 12:16:14.764106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0c6e62db04d'
down_revision = '5fcf03a426b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add heading metadata to document_chunks table.
    
    Adds:
    - heading: TEXT NULL - The section heading for this chunk
    - char_start: INTEGER NULL - Start position of chunk in original text
    - char_end: INTEGER NULL - End position of chunk in original text
    - Index on (company_id, document_id) for faster filtering
    """
    # Add heading column
    op.add_column('document_chunks', sa.Column('heading', sa.Text(), nullable=True))
    
    # Add char_start column
    op.add_column('document_chunks', sa.Column('char_start', sa.Integer(), nullable=True))
    
    # Add char_end column
    op.add_column('document_chunks', sa.Column('char_end', sa.Integer(), nullable=True))
    
    # Create index on (company_id, document_id) for faster filtering
    op.create_index(
        'ix_document_chunks_company_document',
        'document_chunks',
        ['company_id', 'document_id']
    )


def downgrade() -> None:
    """
    Remove heading metadata from document_chunks table.
    """
    # Drop index
    op.drop_index('ix_document_chunks_company_document', table_name='document_chunks')
    
    # Drop columns
    op.drop_column('document_chunks', 'char_end')
    op.drop_column('document_chunks', 'char_start')
    op.drop_column('document_chunks', 'heading')
