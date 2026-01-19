"""Text chunking service."""
from typing import List
import re


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk in characters (default: 1000)
        overlap: Number of characters to overlap between chunks (default: 150)
        
    Returns:
        List of text chunks
    """
    if not text or len(text.strip()) == 0:
        return []
    
    # Remove excessive whitespace but preserve structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    chunks = []
    current_pos = 0
    text_length = len(text)
    
    # Try to split by paragraphs first (double newline)
    paragraphs = text.split('\n\n')
    
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_length = len(para)
        
        # If paragraph fits in current chunk, add it
        if current_length + para_length + 2 <= chunk_size:  # +2 for \n\n
            current_chunk.append(para)
            current_length += para_length + 2
        else:
            # Save current chunk if it has content
            if current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)
            
            # If paragraph itself is larger than chunk_size, split it by sentences
            if para_length > chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_chunk = []
                current_length = 0
                
                for sentence in sentences:
                    sent_length = len(sentence)
                    if current_length + sent_length + 1 <= chunk_size:
                        current_chunk.append(sentence)
                        current_length += sent_length + 1
                    else:
                        if current_chunk:
                            chunk_text = ' '.join(current_chunk)
                            chunks.append(chunk_text)
                            # Add overlap: keep last 'overlap' chars
                            if len(chunk_text) > overlap:
                                current_chunk = [chunk_text[-overlap:], sentence]
                                current_length = overlap + sent_length + 1
                            else:
                                current_chunk = [sentence]
                                current_length = sent_length + 1
                        else:
                            # Sentence too long, split by words
                            words = sentence.split()
                            for word in words:
                                word_length = len(word) + 1
                                if current_length + word_length <= chunk_size:
                                    current_chunk.append(word)
                                    current_length += word_length
                                else:
                                    if current_chunk:
                                        chunks.append(' '.join(current_chunk))
                                        # Overlap
                                        if len(current_chunk) > 10:  # Rough overlap in words
                                            current_chunk = current_chunk[-5:]
                                            current_length = sum(len(w) for w in current_chunk) + len(current_chunk)
                                    current_chunk = [word]
                                    current_length = word_length
            else:
                # Start new chunk with overlap from previous
                if chunks and len(chunks[-1]) > overlap:
                    overlap_text = chunks[-1][-overlap:]
                    current_chunk = [overlap_text, para]
                    current_length = overlap + para_length + 2
                else:
                    current_chunk = [para]
                    current_length = para_length
    
    # Add final chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk) if isinstance(current_chunk[0], str) and '\n\n' in current_chunk[0] else ' '.join(current_chunk)
        chunks.append(chunk_text)
    
    # Ensure chunks are within size limits
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            final_chunks.append(chunk)
        else:
            # Split oversized chunk
            while len(chunk) > chunk_size:
                final_chunks.append(chunk[:chunk_size])
                chunk = chunk[chunk_size - overlap:]
            if chunk:
                final_chunks.append(chunk)
    
    return [c.strip() for c in final_chunks if c.strip()]
