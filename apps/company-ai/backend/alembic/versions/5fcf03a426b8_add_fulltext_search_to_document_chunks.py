"""add_fulltext_search_to_document_chunks

Revision ID: 5fcf03a426b8
Revises: baf1b3045e48
Create Date: 2026-01-18 12:04:18.469160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fcf03a426b8'
down_revision = 'baf1b3045e48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add full-text search support to document_chunks table.
    
    Adds:
    - text_tsv: GENERATED tsvector column for English full-text search
    - GIN index on text_tsv for fast lexical search
    """
    # Add GENERATED tsvector column for full-text search
    # This column is automatically computed from the text column using English config
    op.execute("""
        ALTER TABLE document_chunks
        ADD COLUMN text_tsv tsvector
        GENERATED ALWAYS AS (to_tsvector('english', text)) STORED;
    """)
    
    # Create GIN index on text_tsv for fast full-text search queries
    op.create_index(
        'ix_document_chunks_text_tsv',
        'document_chunks',
        ['text_tsv'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Remove full-text search support from document_chunks table.
    """
    # Drop GIN index
    op.drop_index('ix_document_chunks_text_tsv', table_name='document_chunks')
    
    # Drop tsvector column
    op.drop_column('document_chunks', 'text_tsv')
