"""RAG (Retrieval-Augmented Generation) service."""
import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.models.document_chunk import DocumentChunk
from app.db.models.document import Document
from app.services.embeddings import embedder
from app.services.llm import llm_client

logger = logging.getLogger(__name__)


def perform_semantic_search(
    query: str,
    company_id: str,
    top_k: int,
    db: Session,
    document_id: Optional[str] = None
) -> List[Dict]:
    """
    Perform hybrid retrieval (semantic + lexical) and return chunks with metadata.
    
    Hybrid retrieval combines:
    - Semantic similarity (pgvector cosine distance)
    - Lexical relevance (PostgreSQL full-text search / BM25-style ranking)
    
    Algorithm:
    1. Embed query → query_vector
    2. Convert query to tsquery using plainto_tsquery
    3. Fetch Top-K candidates using vector similarity (e.g. 20)
    4. For candidates, compute hybrid score:
       - semantic_score = 1 - (embedding <=> query_vector)
       - lexical_score = ts_rank_cd(text_tsv, tsquery)
       - final_score = 0.7 * semantic_score + 0.3 * lexical_score
    5. Return best N ordered by final_score DESC
    
    Args:
        query: Search query text
        company_id: Company UUID string
        top_k: Number of results to return (final count)
        db: Database session
        document_id: Optional document ID filter
        
    Returns:
        List of chunk dictionaries with metadata and hybrid scores
    """
    # Step 1: Generate embedding for query
    query_embedding = embedder.embed(query)
    
    if not query_embedding or len(query_embedding) != 768:
        logger.error("Failed to generate valid embedding for query")
        return []
    
    # Step 2: Convert query to tsquery for full-text search
    # plainto_tsquery handles plain text and converts to tsquery format
    # We'll use this in the SQL query
    
    # Step 3: Fetch more candidates than needed (e.g. 20) for reranking
    # This allows us to find lexically relevant chunks that might have lower semantic similarity
    candidate_limit = max(top_k * 4, 20)  # Fetch 4x candidates or minimum 20
    
    # Build base WHERE clause
    base_where = "dc.company_id = CAST(:company_id AS uuid)"
    params = {
        "query_vec": str(query_embedding),
        "company_id": company_id,
        "query_text": query,
        "candidate_limit": candidate_limit
    }
    
    # Optional document filter
    if document_id:
        try:
            base_where += " AND dc.document_id = CAST(:document_id AS uuid)"
            params["document_id"] = document_id
        except Exception:
            pass
    
    # Step 4: Hybrid retrieval SQL query
    # This query:
    # - Pre-filters by company_id (and optionally document_id)
    # - Gets Top-K candidates using vector similarity
    # - Computes semantic_score and lexical_score
    # - Combines scores with weighted average (0.7 semantic + 0.3 lexical)
    # - Returns best N ordered by final_score
    
    query_str = f"""
    WITH candidates AS (
        -- Step A: Get Top-K semantic candidates
        SELECT 
            dc.id,
            dc.document_id,
            dc.chunk_index,
            dc.text,
            dc.token_estimate,
            dc.text_tsv,
            dc.heading,
            1 - (dc.embedding <=> CAST(:query_vec AS vector)) as semantic_score
        FROM document_chunks dc
        WHERE {base_where}
        ORDER BY semantic_score DESC
        LIMIT :candidate_limit
    ),
    query_tsquery AS (
        -- Convert query to tsquery once for reuse
        SELECT plainto_tsquery('english', :query_text) as tsquery
    )
    SELECT 
        c.id,
        c.document_id,
        c.chunk_index,
        c.text,
        c.token_estimate,
        c.heading,
        c.semantic_score,
        -- Step B: Compute lexical score using ts_rank_cd
        COALESCE(ts_rank_cd(c.text_tsv, qt.tsquery), 0.0) as lexical_score,
        -- Step C: Final hybrid score: 0.7 * semantic + 0.3 * lexical
        (0.7 * c.semantic_score + 0.3 * COALESCE(ts_rank_cd(c.text_tsv, qt.tsquery), 0.0)) as final_score
    FROM candidates c
    CROSS JOIN query_tsquery qt
    ORDER BY final_score DESC
    LIMIT :top_k
    """
    
    params["top_k"] = top_k
    
    # Execute hybrid search
    try:
        result = db.execute(text(query_str), params)
        rows = result.fetchall()
    except Exception as e:
        logger.error(f"Hybrid search query failed: {e}")
        # Fallback to pure semantic search if hybrid fails
        logger.info("Falling back to pure semantic search")
        return _fallback_semantic_search(query, query_embedding, company_id, top_k, db, document_id)
    
    if not rows:
        return []
    
    # Get document IDs for filename lookup
    document_ids = [str(row[1]) for row in rows]
    documents = {
        str(doc.id): doc.filename_original
        for doc in db.query(Document).filter(Document.id.in_(document_ids)).all()
    }
    
    # Build results with hybrid scores
    chunks = []
    for row in rows:
        chunk_id, doc_id, chunk_index, text_content, token_estimate, heading, semantic_score, lexical_score, final_score = row
        document_filename = documents.get(str(doc_id), "Unknown")
        
        chunks.append({
            "chunk_id": str(chunk_id),
            "document_id": str(doc_id),
            "document_filename": document_filename,
            "chunk_index": chunk_index,
            "text": text_content,
            "heading": heading,  # Section heading for this chunk
            "similarity_score": float(final_score),  # Use final_score as similarity_score for compatibility
            "semantic_score": float(semantic_score),
            "lexical_score": float(lexical_score),
            "token_estimate": token_estimate
        })
    
    return chunks


def _fallback_semantic_search(
    query: str,
    query_embedding: List[float],
    company_id: str,
    top_k: int,
    db: Session,
    document_id: Optional[str] = None
) -> List[Dict]:
    """
    Fallback to pure semantic search if hybrid search fails.
    Used internally when full-text search is not available.
    """
    base_where = "dc.company_id = CAST(:company_id AS uuid)"
    params = {
        "query_vec": str(query_embedding),
        "company_id": company_id,
        "limit": top_k
    }
    
    if document_id:
        try:
            base_where += " AND dc.document_id = CAST(:document_id AS uuid)"
            params["document_id"] = document_id
        except Exception:
            pass
    
    query_str = f"""
    SELECT 
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.text,
        dc.token_estimate,
        dc.heading,
        1 - (dc.embedding <=> CAST(:query_vec AS vector)) as similarity
    FROM document_chunks dc
    WHERE {base_where}
    ORDER BY similarity DESC
    LIMIT :limit
    """
    
    result = db.execute(text(query_str), params)
    rows = result.fetchall()
    
    if not rows:
        return []
    
    document_ids = [str(row[1]) for row in rows]
    documents = {
        str(doc.id): doc.filename_original
        for doc in db.query(Document).filter(Document.id.in_(document_ids)).all()
    }
    
    chunks = []
    for row in rows:
        chunk_id, doc_id, chunk_index, text_content, token_estimate, heading, similarity = row
        document_filename = documents.get(str(doc_id), "Unknown")
        
        chunks.append({
            "chunk_id": str(chunk_id),
            "document_id": str(doc_id),
            "document_filename": document_filename,
            "chunk_index": chunk_index,
            "text": text_content,
            "heading": heading,  # Section heading for this chunk
            "similarity_score": float(similarity),
            "token_estimate": token_estimate
        })
    
    return chunks


def build_rag_prompt(context_chunks: List[Dict], user_question: str) -> str:
    """
    Build the RAG prompt with system instructions, context, and user question.
    
    Args:
        context_chunks: List of chunk dictionaries with text and metadata
        user_question: The user's question
        
    Returns:
        Complete prompt string
    """
    # System prompt
    system_prompt = """You are a company AI assistant. Your role is to answer questions based ONLY on the provided context from company documents.

CRITICAL RULES - STRICT ENFORCEMENT:

1. Answer ONLY using DIRECT, EXPLICIT information from the provided context below.
   - Use ONLY information that is clearly stated in the context.
   - Do NOT infer, imply, or speculate.
   - Do NOT connect indirectly related sections.
   - Do NOT guess intent or meaning.

2. FORBIDDEN LANGUAGE - NEVER USE:
   - "This might imply..."
   - "This could suggest..."
   - "Based on related sections..."
   - "It may be assumed..."
   - "This might mean..."
   - "This could indicate..."
   - Any form of speculation or inference

3. If the answer is not EXPLICITLY in the context:
   - You MUST say: "I don't have enough information in the uploaded documents to answer this question."
   - You MAY mention which documents were checked (if any chunks were retrieved).
   - You MAY suggest uploading the relevant policy/document.
   - You MUST NOT infer or imply an answer from related but non-direct information.

4. Do NOT use any knowledge outside of the provided context.

5. Do NOT make up or guess information.

6. Cite which document the information comes from when possible.

7. If you retrieved chunks but they don't directly answer the question:
   - State clearly that the documents don't contain the requested information.
   - Do NOT try to infer an answer from tangentially related content.

Context from company documents:
"""
    
    # Build context block
    # Remove chunk IDs from user-facing output - use section headings instead
    context_block = ""
    for chunk in context_chunks:
        doc_name = chunk["document_filename"]
        chunk_text = chunk["text"]
        heading = chunk.get("heading")
        
        # Format: [Document: filename — Section X: Heading] or [Document: filename]
        if heading:
            context_block += f"\n[Document: {doc_name} — Section: {heading}]\n{chunk_text}\n"
        else:
            context_block += f"\n[Document: {doc_name}]\n{chunk_text}\n"
    
    # Trim context if too long
    if len(context_block) > settings.RAG_MAX_CONTEXT_CHARS:
        context_block = context_block[:settings.RAG_MAX_CONTEXT_CHARS]
        context_block += "\n[... context truncated ...]"
    
    # User question with strict reminder
    user_prompt = f"\n\nQuestion: {user_question}\n\nAnswer based ONLY on EXPLICIT information in the context above. Do NOT infer, imply, or speculate. If the answer is not directly stated, say you don't have enough information."
    
    # Combine
    full_prompt = system_prompt + context_block + user_prompt
    
    return full_prompt


def answer_question(
    query: str,
    company_id: str,
    db: Session,
    top_k: Optional[int] = None
) -> Tuple[str, List[Dict], List[Dict], str, int]:
    """
    Answer a question using RAG (Retrieval-Augmented Generation).
    
    Args:
        query: User's question
        company_id: Company UUID string
        db: Database session
        top_k: Number of chunks to retrieve (defaults to settings.RAG_TOP_K)
        
    Returns:
        Tuple of (answer, citations, sources, confidence, used_chunks)
        - answer: Cleaned answer text
        - citations: List of citation dicts (backward compatibility)
        - sources: List of source dicts with quotes (new format)
        - confidence: Confidence level string
        - used_chunks: Number of chunks used
    """
    top_k = top_k or settings.RAG_TOP_K
    
    # Perform semantic search
    chunks = perform_semantic_search(query, company_id, top_k, db)
    
    # Safety check: if no chunks or very low similarity, return safe fallback
    if not chunks:
        return (
            "I don't have enough information in the uploaded documents to answer this question.",
            [],
            [],  # Empty sources list
            "none",
            0
        )
    
    # Check if similarity scores are too low (threshold: 0.3)
    # Low similarity means chunks are not directly relevant - do not allow inference
    max_similarity = max(chunk["similarity_score"] for chunk in chunks)
    if max_similarity < 0.3:
        return (
            "I don't have enough information in the uploaded documents to answer this question. The available documents do not contain information directly related to this topic.",
            [],
            [],  # Empty sources list
            "low",
            0
        )
    
    # Build prompt
    prompt = build_rag_prompt(chunks, query)
    
    # Generate answer
    answer = llm_client.generate(prompt)
    
    if not answer:
        return (
            "I encountered an error while generating a response. Please try again.",
            [],
            [],  # Empty sources list
            "error",
            0
        )
    
    # Determine confidence based on similarity scores
    avg_similarity = sum(chunk["similarity_score"] for chunk in chunks) / len(chunks)
    if avg_similarity >= 0.7:
        confidence = "high"
    elif avg_similarity >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Clean answer text to remove citation noise
    cleaned_answer = _clean_answer_text(answer)
    
    # Build and deduplicate citations with quotes
    # CRITICAL: Extract quotes ONLY from chunks that were actually used to generate the answer
    # These are the chunks passed to the LLM in the prompt (the 'chunks' variable)
    # We must NOT extract from low-score chunks or unused context
    
    # Extract answer keywords for relevance filtering (use cleaned answer)
    answer_keywords = _extract_answer_keywords(cleaned_answer)
    
    # Deduplicate by (document_id + heading) to merge quotes from multiple chunks
    sources_map = {}  # Key: (document_id, heading), Value: source dict with quotes list
    
    # Only process chunks that were actually used (passed to LLM)
    for chunk in chunks:
        doc_id = chunk["document_id"]
        doc_filename = chunk["document_filename"]
        heading = chunk.get("heading")
        chunk_text = chunk["text"]
        source_key = (doc_id, heading)
        
        # Extract quotes from this chunk
        candidate_quotes = _extract_quotes(chunk_text, max_quotes=2, max_length=220)
        
        # Filter quotes by relevance to the answer
        # Only keep quotes that contain at least one answer keyword
        relevant_quotes = [
            quote for quote in candidate_quotes
            if _quote_is_relevant(quote, answer_keywords)
        ]
        
        # If no relevant quotes found, skip this chunk (it doesn't support the answer)
        if not relevant_quotes:
            continue
        
        if source_key not in sources_map:
            # First occurrence of this (document, section) pair
            sources_map[source_key] = {
                "document_id": doc_id,
                "document_filename": doc_filename,
                "heading": heading,
                "quotes": relevant_quotes,
                "chunk_index": chunk["chunk_index"],
                "similarity_score": chunk["similarity_score"]
            }
        else:
            # Merge quotes from multiple chunks of same (document + heading)
            existing_quotes = sources_map[source_key]["quotes"]
            # Add new quotes, avoiding duplicates
            for quote in relevant_quotes:
                # Simple deduplication: if quote is very similar (80% overlap), skip
                is_duplicate = False
                for existing_quote in existing_quotes:
                    # Check if quotes are very similar (simple character overlap check)
                    shorter = min(len(quote), len(existing_quote))
                    longer = max(len(quote), len(existing_quote))
                    if shorter > 0 and longer > 0:
                        # Simple substring check for near-duplicates
                        if quote in existing_quote or existing_quote in quote:
                            is_duplicate = True
                            break
                        # Check character overlap (rough estimate)
                        common_chars = sum(1 for c in quote if c in existing_quote)
                        if common_chars / shorter > 0.8:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    existing_quotes.append(quote)
            
            # Limit to max 3 quotes per source (keep most relevant/shortest)
            if len(existing_quotes) > 3:
                # Sort by length (shorter = more concise = better)
                existing_quotes.sort(key=len)
                existing_quotes = existing_quotes[:3]
            
            sources_map[source_key]["quotes"] = existing_quotes
            
            # Update similarity score if this chunk has higher score
            if chunk["similarity_score"] > sources_map[source_key]["similarity_score"]:
                sources_map[source_key]["similarity_score"] = chunk["similarity_score"]
    
    # Sort sources by similarity score (highest first)
    sorted_sources = sorted(
        sources_map.values(),
        key=lambda x: x["similarity_score"],
        reverse=True
    )
    
    # Convert to list for citations (backward compatibility)
    citations = [
        {
            "document_id": src["document_id"],
            "document_filename": src["document_filename"],
            "heading": src["heading"],
            "chunk_index": src["chunk_index"]
        }
        for src in sorted_sources
    ]
    
    # Build sources list with quotes (new format)
    # Remove internal similarity_score before returning
    sources = [
        {
            "document_id": src["document_id"],
            "filename": src["document_filename"],
            "heading": src["heading"],
            "quotes": src["quotes"]
        }
        for src in sorted_sources
    ]
    
    return cleaned_answer, citations, sources, confidence, len(chunks)


def _extract_answer_keywords(answer: str) -> set:
    """
    Extract keywords from the answer for relevance filtering.
    
    Extracts:
    - Nouns and important words (excluding common stop words)
    - Numbers (e.g., "2", "days", "week")
    - Key phrases
    
    Args:
        answer: The generated answer text
        
    Returns:
        Set of lowercase keywords
    """
    import re
    
    if not answer:
        return set()
    
    # Common stop words to exclude
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "can", "this",
        "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "what", "which", "who", "where", "when", "why", "how", "if", "then",
        "than", "more", "most", "less", "least", "very", "much", "many",
        "some", "any", "all", "each", "every", "no", "not", "only", "just"
    }
    
    # Convert to lowercase
    text = answer.lower()
    
    # Extract words (alphanumeric sequences)
    words = re.findall(r'\b[a-z0-9]+\b', text)
    
    # Filter out stop words and very short words (1-2 chars)
    keywords = {w for w in words if w not in stop_words and len(w) > 2}
    
    # Also extract numbers and important phrases
    numbers = re.findall(r'\b\d+\b', answer)
    keywords.update(numbers)
    
    return keywords


def _quote_is_relevant(quote: str, answer_keywords: set) -> bool:
    """
    Check if a quote is relevant to the answer by checking for keyword overlap.
    
    A quote is relevant if it contains at least one keyword from the answer.
    This ensures quotes directly support the answer, not just come from retrieved chunks.
    
    Args:
        quote: The quote text to check
        answer_keywords: Set of keywords extracted from the answer
        
    Returns:
        True if quote contains at least one answer keyword, False otherwise
    """
    if not quote or not answer_keywords:
        return False
    
    import re
    
    # Convert quote to lowercase for comparison
    quote_lower = quote.lower()
    
    # Check if any keyword appears in the quote
    for keyword in answer_keywords:
        # Use word boundary to match whole words
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, quote_lower):
            return True
    
    return False


def _extract_quotes(chunk_text: str, max_quotes: int = 2, max_length: int = 220) -> List[str]:
    """
    Extract 1-2 supporting quotes from chunk text.
    
    Rules:
    - Quotes must be exact substrings of the chunk text
    - Prefer full sentences (split by . ! ?)
    - Max 220 characters per quote
    - If no clean sentence boundaries exist, fall back to first 200 chars
    - Never invent text, never paraphrase
    
    Args:
        chunk_text: The chunk text to extract quotes from
        max_quotes: Maximum number of quotes to extract (default 2)
        max_length: Maximum length per quote in characters (default 220)
        
    Returns:
        List of quote strings (1-2 quotes, each <= max_length chars)
    """
    if not chunk_text or not chunk_text.strip():
        return []
    
    import re
    
    # Clean the text
    text = chunk_text.strip()
    
    # Try to split by sentence boundaries (. ! ? followed by space or end)
    # This regex matches sentence endings
    sentences = re.split(r'([.!?]\s+|\.$)', text)
    
    # Reconstruct sentences (split includes delimiters)
    reconstructed = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
        else:
            sentence = sentences[i]
        sentence = sentence.strip()
        if sentence:
            reconstructed.append(sentence)
    
    # If we have clean sentences, use them
    if reconstructed:
        quotes = []
        for sentence in reconstructed:
            if len(sentence) <= max_length:
                quotes.append(sentence)
                if len(quotes) >= max_quotes:
                    break
            elif len(quotes) == 0:  # If first sentence is too long, truncate it
                # Truncate at word boundary if possible
                truncated = sentence[:max_length]
                last_space = truncated.rfind(' ')
                if last_space > max_length * 0.7:  # Only truncate at word if we keep >70% of max
                    truncated = truncated[:last_space] + '...'
                else:
                    truncated = truncated.rstrip() + '...'
                quotes.append(truncated)
                break
        
        if quotes:
            return quotes[:max_quotes]
    
    # Fallback: if no clean sentences or all too long, take first 200 chars
    # Try to break at word boundary
    if len(text) > max_length:
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:
            truncated = truncated[:last_space] + '...'
        else:
            truncated = truncated.rstrip() + '...'
        return [truncated]
    else:
        return [text]


def _clean_answer_text(answer: str) -> str:
    """
    Clean answer text to remove citation noise and verbose preambles.
    
    Removes:
    - "According to Document: ..." type phrases
    - "As stated in Chunk: ..." type phrases
    - "I've checked the provided documents..." type verbose preambles
    - "Document checked: ..." debug text (CRITICAL: must never appear in enterprise UI)
    - Any mention of "Chunk" or UUIDs
    
    Args:
        answer: Raw answer text from LLM
        
    Returns:
        Cleaned answer text
    """
    if not answer:
        return answer
    
    import re
    
    # Remove verbose preambles
    preambles = [
        r"I've (checked|searched|reviewed) (through |)the (provided |)documents?.*?(?=\.|:|\n)",
        r"I've found relevant information.*?(?=\.|:|\n)",
        r"According to (Document|Chunk).*?(?=\.|:|\n)",
        r"As stated in (Document|Chunk).*?(?=\.|:|\n)",
        r"Based on (Document|Chunk).*?(?=\.|:|\n)",
        r"Document checked:.*?(?=\.|:|\n)",  # CRITICAL: Remove "Document checked" debug text
        r"Documents? (checked|reviewed|searched):.*?(?=\.|:|\n)",
    ]
    
    cleaned = answer
    for pattern in preambles:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove chunk ID references (UUIDs)
    uuid_pattern = r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'
    cleaned = re.sub(uuid_pattern, "", cleaned, flags=re.IGNORECASE)
    
    # Remove "Chunk: ..." references
    cleaned = re.sub(r'Chunk:\s*[^\s,]+', "", cleaned, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned
