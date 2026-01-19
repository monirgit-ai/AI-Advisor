"""Heading detection service for document chunking."""
from typing import List, Tuple, Optional, Dict
import re
from app.services.chunking import chunk_text


def is_heading(line: str) -> bool:
    """
    Detect if a line is a heading using MVP rules.
    
    Rules:
    A) Starts with numbering: ^\d+(\.\d+)*\s+
       Example: "1. Leave Policy", "2.1 Incident Reporting"
    B) Ends with colon ':' and length < 120
       Example: "Incident Reporting:"
    C) ALL CAPS (letters + spaces) and length < 80
       Example: "ACCESS CONTROL"
    
    Args:
        line: The line to check
        
    Returns:
        True if line matches heading pattern, False otherwise
    """
    line = line.strip()
    
    if not line:
        return False
    
    # Rule A: Numbered headings (e.g., "1. ", "2.1 ", "3.2.1 ")
    if re.match(r'^\d+(\.\d+)*\s+', line):
        return True
    
    # Rule B: Ends with colon and length < 120
    if line.endswith(':') and len(line) < 120:
        return True
    
    # Rule C: ALL CAPS (letters + spaces only) and length < 80
    if len(line) < 80 and line.isupper() and re.match(r'^[A-Z\s]+$', line):
        return True
    
    return False


def extract_headings(text: str) -> Dict[int, str]:
    """
    Extract headings from text and map them to character positions.
    
    Args:
        text: The full text to analyze
        
    Returns:
        Dictionary mapping character positions (line starts) to heading text
    """
    heading_map = {}
    lines = text.split('\n')
    current_heading = None
    char_pos = 0
    
    for line in lines:
        line_start = char_pos
        
        if is_heading(line):
            # Clean heading (remove numbering prefix if present)
            heading_clean = re.sub(r'^\d+(\.\d+)*\s+', '', line).strip()
            # Remove trailing colon if present
            if heading_clean.endswith(':'):
                heading_clean = heading_clean[:-1].strip()
            current_heading = heading_clean if heading_clean else line.strip()
        
        # Store heading for this line's start position
        heading_map[line_start] = current_heading
        
        # Move to next line (include newline character)
        char_pos += len(line) + 1
    
    return heading_map


def find_heading_for_position(heading_map: Dict[int, str], position: int) -> Optional[str]:
    """
    Find the most recent heading before a given position.
    
    Args:
        heading_map: Dictionary mapping character positions to headings
        position: Character position to find heading for
        
    Returns:
        Most recent heading before position, or None if not found
    """
    if not heading_map:
        return None
    
    # Find the highest position <= position that has a heading
    valid_positions = [pos for pos in heading_map.keys() if pos <= position]
    if not valid_positions:
        return None
    
    closest_pos = max(valid_positions)
    return heading_map.get(closest_pos)


def chunk_text_with_headings(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> List[Tuple[str, int, int, Optional[str]]]:
    """
    Chunk text and attach heading metadata and position offsets.
    
    Uses the existing chunk_text function and then maps headings to chunks
    by finding chunk positions in the original text.
    
    Args:
        text: The full text to chunk
        chunk_size: Target size of each chunk in characters (default: 1000)
        overlap: Number of characters to overlap between chunks (default: 150)
        
    Returns:
        List of tuples: (chunk_text, char_start, char_end, heading)
        heading is None if no heading found for that chunk
    """
    if not text or len(text.strip()) == 0:
        return []
    
    # Extract headings from text
    heading_map = extract_headings(text)
    
    # Use existing chunking function
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    
    # Map chunks to headings and positions
    result = []
    search_start = 0
    
    for chunk in chunks:
        # Find this chunk's position in the original text
        chunk_start = text.find(chunk, search_start)
        if chunk_start == -1:
            # Fallback: use search_start if exact match not found
            chunk_start = search_start
        
        chunk_end = chunk_start + len(chunk)
        search_start = chunk_start + 1  # Move forward for next search
        
        # Find heading for this chunk
        chunk_heading = find_heading_for_position(heading_map, chunk_start)
        
        result.append((chunk, chunk_start, chunk_end, chunk_heading))
    
    return result
