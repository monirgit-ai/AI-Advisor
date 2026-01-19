"""Semantic search endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_user
from app.services.rag import perform_semantic_search
import uuid

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    document_id: Optional[str] = Field(None, description="Optional: filter by document ID")


class SearchResult(BaseModel):
    """Search result model."""
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    similarity_score: float
    document_filename: str
    token_estimate: Optional[int] = None


class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult]
    total_results: int


@router.post("", response_model=SearchResponse)
async def search(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hybrid search (semantic + lexical) across company documents.
    
    Uses hybrid retrieval combining:
    - Semantic similarity (pgvector cosine distance)
    - Lexical relevance (PostgreSQL full-text search)
    
    Args:
        search_request: Search query and parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of matching chunks with hybrid similarity scores
    """
    # Validate document_id if provided
    document_id = None
    if search_request.document_id:
        try:
            doc_uuid = uuid.UUID(search_request.document_id)
            document_id = str(doc_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document_id format"
            )
    
    # Use hybrid search from RAG service
    # This combines semantic (vector) and lexical (full-text) search
    chunks = perform_semantic_search(
        query=search_request.query,
        company_id=str(current_user.company_id),
        top_k=search_request.top_k,
        db=db,
        document_id=document_id
    )
    
    # Convert to SearchResult format
    results = [
        SearchResult(
            chunk_id=chunk["chunk_id"],
            document_id=chunk["document_id"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            similarity_score=chunk["similarity_score"],  # This is now the hybrid final_score
            document_filename=chunk["document_filename"],
            heading=chunk.get("heading"),  # Section heading for this chunk
            token_estimate=chunk.get("token_estimate")
        )
        for chunk in chunks
    ]
    
    return SearchResponse(
        results=results,
        total_results=len(results)
    )
