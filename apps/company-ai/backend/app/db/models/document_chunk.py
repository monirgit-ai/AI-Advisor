"""Document chunk model for RAG."""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from app.db.base import Base


class DocumentChunk(Base):
    """Document chunk model for RAG indexing."""
    
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    text = Column(Text, nullable=False)
    token_estimate = Column(Integer, nullable=True)  # Simple estimate: ~4 chars per token
    embedding = Column(Vector(768), nullable=False)  # Fixed 768 dimensions for nomic-embed-text
    heading = Column(Text, nullable=True)  # Section heading for this chunk
    char_start = Column(Integer, nullable=True)  # Start position of chunk in original text
    char_end = Column(Integer, nullable=True)  # End position of chunk in original text
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", backref="document_chunks")
    document = relationship("Document", backref="chunks")
