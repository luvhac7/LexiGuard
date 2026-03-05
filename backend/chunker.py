from typing import List

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Exact parameters as specified
CHUNK_SIZE_WORDS = 800  # ~3000 characters
CHUNK_OVERLAP_WORDS = 150  # ~600 characters
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text_recursive(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Chunk text using LangChain RecursiveCharacterTextSplitter if available,
    otherwise fallback to manual implementation.
    """
    # Approximate: 800 words ≈ 3000 chars, 150 words ≈ 600 chars
    chunk_size = chunk_size or 3000
    chunk_overlap = chunk_overlap or 600
    
    if LANGCHAIN_AVAILABLE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=SEPARATORS,
            length_function=len,
        )
        chunks = splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    else:
        # Fallback manual implementation
        return _manual_split(text, chunk_size, chunk_overlap)


def _manual_split(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Manual recursive splitting when LangChain not available."""
    def split_on_sep(t: str, seps: List[str], size: int) -> List[str]:
        if not t:
            return []
        if not seps:
            return [t[i:i+size] for i in range(0, len(t), size)]
        
        sep = seps[0]
        pieces = t.split(sep) if sep else list(t)
        chunks: List[str] = []
        current = ""
        
        for piece in pieces:
            candidate = (current + (sep if current and sep else "") + piece) if sep else (current + piece)
            
            if len(candidate) <= size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # If single piece too large, recurse
                if len(piece) > size:
                    chunks.extend(split_on_sep(piece, seps[1:], size))
                    current = ""
                else:
                    current = piece
        
        if current:
            chunks.append(current)
        return chunks

    primaries = split_on_sep(text, SEPARATORS, chunk_size)
    if not chunk_overlap:
        return [c.strip() for c in primaries if c.strip()]

    # Apply overlap
    overlapped: List[str] = []
    prev = ""
    for ch in primaries:
        if prev and chunk_overlap:
            start = max(0, len(prev) - chunk_overlap)
            prefix = prev[start:]
            merged = (prefix + ch) if len(prefix) + len(ch) <= chunk_size + chunk_overlap else ch
            overlapped.append(merged.strip())
        else:
            overlapped.append(ch.strip())
        prev = ch

    # Final trimming to chunk_size
    final: List[str] = []
    for ch in overlapped:
        if len(ch) <= chunk_size:
            if ch:
                final.append(ch)
        else:
            # Further split oversized chunks
            final.extend([ch[i:i+chunk_size].strip() for i in range(0, len(ch), chunk_size - chunk_overlap)])
    
    return [c for c in final if c]
