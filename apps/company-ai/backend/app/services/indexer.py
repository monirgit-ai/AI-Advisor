"""Document indexing service."""
import logging
from sqlalchemy.orm import Session
from typing import Tuple, Optional
from app.db.models.document import Document, IndexStatus
from app.db.models.document_chunk import DocumentChunk
from app.services.chunking import chunk_text
from app.services.heading_detection import chunk_text_with_headings
from app.services.embeddings import embedder

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Simple token estimate: ~4 characters per token.
    
    Args:
        text: The text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def index_document(document_id: str, company_id: str, db: Session) -> Tuple[bool, Optional[str], int]:
    """
    Index a document: chunk, embed, and store chunks.
    
    Args:
        document_id: UUID of the document to index
        company_id: UUID of the company (for validation)
        db: Database session
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str], chunks_created: int)
    """
    # Load document
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        return False, "Document not found", 0
    
    # Validate company_id
    if str(document.company_id) != company_id:
        return False, "Document does not belong to company", 0
    
    # Check if document has text
    if not document.text_extracted:
        return False, "Document has no extracted text", 0
    
    try:
        # Update status to indexing
        document.index_status = IndexStatus.INDEXING
        document.index_error = None
        db.commit()
        
        # Delete existing chunks for this document
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()
        db.commit()
        
        # Chunk the text with heading metadata
        chunks_with_metadata = chunk_text_with_headings(
            document.text_extracted,
            chunk_size=1000,
            overlap=150
        )
        
        if not chunks_with_metadata:
            document.index_status = IndexStatus.NOT_INDEXED
            document.index_error = "No chunks generated from document text"
            db.commit()
            return False, "No chunks generated", 0
        
        # Extract chunk texts for embedding
        chunks = [chunk_text for chunk_text, _, _, _ in chunks_with_metadata]
        
        # Generate embeddings for all chunks
        embeddings = embedder.embed_batch(chunks)
        
        # Check for failed embeddings
        failed_count = sum(1 for e in embeddings if e is None)
        if failed_count == len(embeddings):
            document.index_status = IndexStatus.FAILED
            document.index_error = "Failed to generate embeddings for all chunks"
            db.commit()
            return False, "Failed to generate embeddings", 0
        
        # Create chunk records with heading metadata
        chunks_created = 0
        for idx, ((chunk_content, char_start, char_end, heading), embedding) in enumerate(zip(chunks_with_metadata, embeddings)):
            if embedding is None:
                logger.warning(f"Skipping chunk {idx} due to embedding failure")
                continue
            
            # Verify embedding dimension
            if len(embedding) != 768:
                logger.warning(f"Chunk {idx} has wrong dimension: {len(embedding)}")
                continue
            
            chunk = DocumentChunk(
                company_id=document.company_id,
                document_id=document.id,
                chunk_index=idx,
                text=chunk_content,
                token_estimate=estimate_tokens(chunk_content),
                embedding=embedding,
                heading=heading,
                char_start=char_start,
                char_end=char_end
            )
            db.add(chunk)
            chunks_created += 1
        
        db.commit()
        
        # Update document status
        if chunks_created > 0:
            document.index_status = IndexStatus.INDEXED
            document.index_error = None
        else:
            document.index_status = IndexStatus.FAILED
            document.index_error = "No chunks were successfully indexed"
        
        db.commit()
        
        if failed_count > 0:
            logger.warning(f"Successfully indexed {chunks_created} chunks, {failed_count} failed")
        
        return True, None, chunks_created
    
    except Exception as e:
        logger.error(f"Error indexing document {document_id}: {e}", exc_info=True)
        document.index_status = IndexStatus.FAILED
        document.index_error = str(e)
        db.rollback()
        db.commit()
        return False, str(e), 0
