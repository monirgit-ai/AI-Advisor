"""Document model."""
from sqlalchemy import Column, String, BigInteger, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base


class DocumentStatus(str, enum.Enum):
    """Document status enumeration."""
    UPLOADED = "uploaded"
    PARSED = "parsed"
    FAILED = "failed"


class IndexStatus(str, enum.Enum):
    """Document indexing status enumeration."""
    NOT_INDEXED = "not_indexed"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(Base):
    """Document model for file uploads."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    uploaded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    filename_original = Column(String(500), nullable=False)
    filename_stored = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    
    text_extracted = Column(Text, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    error_message = Column(Text, nullable=True)
    
    index_status = Column(Enum(IndexStatus, values_callable=lambda x: [e.value for e in x]), default=IndexStatus.NOT_INDEXED, nullable=False)
    index_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", backref="documents")
    uploaded_by_user = relationship("User", backref="documents")
