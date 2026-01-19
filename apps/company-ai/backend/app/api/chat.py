"""Chat / RAG answer generation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_user
from app.services.rag import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    question: str = Field(..., description="User's question")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of chunks to retrieve (optional)")


class Citation(BaseModel):
    """Citation model (backward compatibility)."""
    document_id: str
    document_filename: str
    heading: Optional[str] = None  # Section heading (e.g., "4. Remote Work Policy")
    chunk_index: Optional[int] = None  # Chunk index for internal reference (not shown in UI)


class Source(BaseModel):
    """Source model with evidence quotes."""
    document_id: str
    filename: str
    heading: Optional[str] = None  # Section heading (e.g., "4. Remote Work Policy")
    quotes: List[str]  # Verbatim quotes from the document (1-3 quotes, each <= 220 chars)


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    citations: List[Citation]  # Backward compatibility (deprecated, use sources)
    sources: List[Source]  # New format with quotes
    confidence: str  # "high", "medium", "low", "none", "error"
    used_chunks: int


@router.post("", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answer a question using RAG (Retrieval-Augmented Generation).
    
    Args:
        chat_request: User's question and optional parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Answer with citations and confidence metadata
    """
    # Answer the question using RAG
    answer, citations, sources, confidence, used_chunks = answer_question(
        query=chat_request.question,
        company_id=str(current_user.company_id),
        db=db,
        top_k=chat_request.top_k
    )
    
    # Convert citations to response format (backward compatibility)
    citation_models = [
        Citation(
            document_id=c["document_id"],
            document_filename=c["document_filename"],
            heading=c.get("heading"),  # Section heading for display
            chunk_index=c.get("chunk_index")  # For internal reference only
        )
        for c in citations
    ]
    
    # Convert sources to response format (new format with quotes)
    source_models = [
        Source(
            document_id=s["document_id"],
            filename=s["filename"],
            heading=s.get("heading"),
            quotes=s.get("quotes", [])
        )
        for s in sources
    ]
    
    return ChatResponse(
        answer=answer,
        citations=citation_models,
        sources=source_models,
        confidence=confidence,
        used_chunks=used_chunks
    )
