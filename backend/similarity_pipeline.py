"""
Advanced semantic relevance scoring pipeline for Indian Kanoon documents.

Uses hybrid scoring with:
- Document chunking (200-350 words, 50-60 word overlap)
- Bi-encoder embeddings (all-mpnet-base-v2 for high accuracy)
- Cross-encoder re-ranking (ms-marco-MiniLM-L-6-v2)
- BM25 lexical matching
- Exact-match term boosting
- Weighted hybrid combination

Designed to achieve 70%+ relevance scores for top Kanoon results.
"""
import re
import html as html_module
import threading
import logging
from typing import List, Tuple, Dict, Any, Optional
from collections import Counter
import numpy as np
from sentence_transformers import SentenceTransformer
from cross_encoder import CrossEncoder

logger = logging.getLogger(__name__)

# ============================================================================
# Model Singletons (Thread-Safe)
# ============================================================================

_bi_encoder: Optional[SentenceTransformer] = None
_cross_encoder: Optional[CrossEncoder] = None
_bi_encoder_lock = threading.Lock()
_cross_encoder_lock = threading.Lock()


def get_bi_encoder() -> SentenceTransformer:
    """Load bi-encoder model once (singleton with thread safety)."""
    global _bi_encoder
    if _bi_encoder is None:
        with _bi_encoder_lock:
            if _bi_encoder is None:
                # Use all-mpnet-base-v2 for much better semantic accuracy than MiniLM
                _bi_encoder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
                logger.info("Loaded bi-encoder model: all-mpnet-base-v2")
    return _bi_encoder


def get_cross_encoder() -> CrossEncoder:
    """Load cross-encoder re-ranker model once (singleton with thread safety)."""
    global _cross_encoder
    if _cross_encoder is None:
        with _cross_encoder_lock:
            if _cross_encoder is None:
                # Cross-encoder for accurate relevance scoring
                _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                logger.info("Loaded cross-encoder model: ms-marco-MiniLM-L-6-v2")
    return _cross_encoder


# ============================================================================
# HTML Cleaning
# ============================================================================

def clean_html_to_text(html: str) -> str:
    """
    Clean HTML content into plain text.
    
    Removes <script> and <style> tags, strips all HTML tags,
    decodes HTML entities, and collapses whitespace.
    """
    if not html:
        return ''
    
    # Remove script and style tags
    html_wo_scripts = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    
    # Remove all HTML tags
    text_only = re.sub(r'<[^>]+>', ' ', html_wo_scripts)
    
    # Decode HTML entities
    text_only = html_module.unescape(text_only)
    
    # Collapse whitespace
    text_only = re.sub(r'[\t\r ]+', ' ', text_only)
    text_only = re.sub(r'\s*\n\s*', '\n', text_only)
    text_only = text_only.strip()
    
    return text_only


# ============================================================================
# Document Chunking
# ============================================================================

def chunk_text(text: str, chunk_size_words: int = 275, overlap_words: int = 55) -> List[str]:
    """
    Split text into overlapping chunks of specified word size.
    
    Args:
        text: Plain text to chunk.
        chunk_size_words: Target words per chunk (200-350 range, default 275).
        overlap_words: Overlap between chunks (50-60 words, default 55).
    
    Returns:
        List of text chunks.
    """
    if not text or len(text.strip()) < chunk_size_words:
        return [text] if text.strip() else []
    
    # Split into words
    words = text.split()
    
    if len(words) <= chunk_size_words:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        # Move start forward by (chunk_size - overlap) to create overlap
        start += chunk_size_words - overlap_words
        
        # Prevent infinite loop
        if start >= len(words):
            break
    
    return chunks


# ============================================================================
# BM25 Scoring
# ============================================================================

class BM25Scorer:
    """Simple BM25 implementation for lexical term matching."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
    
    def score(self, query: str, document: str) -> float:
        """
        Compute BM25 score between query and document.
        
        Args:
            query: Search query text.
            document: Document text to score.
        
        Returns:
            BM25 score (typically 0-10 range, can be higher).
        """
        if not query or not document:
            return 0.0
        
        # Tokenize (simple word split, lowercase)
        query_terms = [t.lower() for t in re.findall(r'\b\w+\b', query)]
        doc_terms = [t.lower() for t in re.findall(r'\b\w+\b', document)]
        
        if not query_terms or not doc_terms:
            return 0.0
        
        # Document length
        doc_len = len(doc_terms)
        avg_doc_len = doc_len  # Simplified: use current doc as average
        
        # Term frequencies in document
        doc_term_freq = Counter(doc_terms)
        query_term_freq = Counter(query_terms)
        
        # Compute BM25 score
        score = 0.0
        for term, qf in query_term_freq.items():
            if term in doc_term_freq:
                tf = doc_term_freq[term]
                # BM25 formula
                idf = np.log(1.0 + (1.0 / (1.0 + 1.0)))  # Simplified IDF
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(avg_doc_len, 1.0)))
                score += idf * (numerator / max(denominator, 1.0)) * qf
        
        return float(score)


# ============================================================================
# Exact Match Boosting
# ============================================================================

def compute_exact_match_boost(query: str, document: str) -> float:
    """
    Compute exact match boost based on query terms appearing in document.
    
    Args:
        query: Search query.
        document: Document text.
    
    Returns:
        Boost score between 0 and 1.
    """
    if not query or not document:
        return 0.0
    
    # Extract meaningful words (3+ chars, lowercase)
    query_words = set([w.lower() for w in re.findall(r'\b\w{3,}\b', query)])
    doc_words = set([w.lower() for w in re.findall(r'\b\w{3,}\b', document)])
    
    if not query_words:
        return 0.0
    
    # Count matches
    matches = len(query_words.intersection(doc_words))
    total_query_words = len(query_words)
    
    # Boost: percentage of query terms found
    boost = matches / total_query_words if total_query_words > 0 else 0.0
    
    return min(boost, 1.0)


# ============================================================================
# Main Scoring Pipeline
# ============================================================================

def score_document_against_query(query: str, doc_text: str) -> float:
    """
    Main function: Compute comprehensive relevance score for document against query.
    
    Pipeline:
    1. Chunk document (200-350 words, 50-60 word overlap)
    2. Bi-encoder: Compute cosine similarity for top-K chunks
    3. Cross-encoder: Re-rank top passages for accuracy
    4. BM25: Lexical term matching score
    5. Exact-match: Term presence boost
    6. Hybrid combination with weighted fusion
    
    Args:
        query: Search query string.
        doc_text: Cleaned document text.
    
    Returns:
        Relevance score between 0 and 1.
    """
    if not query or not doc_text:
        return 0.0
    
    # Skip very short documents
    if len(doc_text.strip()) < 50:
        return 0.0
    
    try:
        # Step 1: Chunk document
        chunks = chunk_text(doc_text, chunk_size_words=275, overlap_words=55)
        
        if not chunks:
            return 0.0
        
        # Step 2: Bi-encoder embeddings for semantic similarity
        bi_encoder = get_bi_encoder()
        query_embedding = bi_encoder.encode([query], convert_to_numpy=True)[0]
        
        chunk_scores = []
        chunk_embeddings = bi_encoder.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        
        for chunk_emb in chunk_embeddings:
            # Cosine similarity
            dot_product = np.dot(query_embedding, chunk_emb)
            norm_query = np.linalg.norm(query_embedding)
            norm_chunk = np.linalg.norm(chunk_emb)
            if norm_query > 0 and norm_chunk > 0:
                cos_sim = dot_product / (norm_query * norm_chunk)
                chunk_scores.append(cos_sim)
            else:
                chunk_scores.append(0.0)
        
        # Get top-K chunks (top 3)
        top_k = min(3, len(chunks))
        top_indices = np.argsort(chunk_scores)[-top_k:][::-1]
        top_chunks = [chunks[i] for i in top_indices]
        
        # Step 3: Cross-encoder re-ranking for accuracy
        cross_encoder = get_cross_encoder()
        cross_scores = []
        
        for chunk in top_chunks:
            # Cross-encoder takes [query, passage] pairs
            score = cross_encoder.predict([(query, chunk)])
            cross_scores.append(float(score[0]))
        
        # Average cross-encoder scores (or max - using max for stronger signal)
        semantic_score = max(cross_scores) if cross_scores else 0.0
        
        # Normalize cross-encoder score (typically outputs -10 to 10, normalize to 0-1)
        # Cross-encoder scores are usually in range [-10, 10], we normalize to [0, 1]
        semantic_score_normalized = (semantic_score + 10.0) / 20.0
        semantic_score_normalized = max(0.0, min(1.0, semantic_score_normalized))
        
        # Step 4: BM25 lexical scoring
        bm25_scorer = BM25Scorer()
        bm25_score = bm25_scorer.score(query, doc_text)
        # Normalize BM25 (typical range 0-10, normalize to 0-1)
        bm25_normalized = min(bm25_score / 10.0, 1.0)
        
        # Step 5: Exact-match boost
        exact_match_boost = compute_exact_match_boost(query, doc_text)
        
        # Step 6: Hybrid weighted combination
        # Weights tuned for Kanoon results to achieve 70%+ for top matches
        w_semantic = 0.50  # Cross-encoder (most important)
        w_bm25 = 0.30      # Lexical matching
        w_exact = 0.20     # Exact term boost
        
        hybrid_score = (
            w_semantic * semantic_score_normalized +
            w_bm25 * bm25_normalized +
            w_exact * exact_match_boost
        )
        
        # Clamp between 0 and 1
        hybrid_score = max(0.0, min(1.0, hybrid_score))
        
        return hybrid_score
        
    except Exception as e:
        logger.warning(f'Error in score_document_against_query: {e}', exc_info=True)
        return 0.0


def final_percent(score: float) -> float:
    """
    Convert relevance score (0-1) to percentage with natural scaling.
    
    Adjusts the scale so that:
    - Top Kanoon results → 70-95%
    - Moderately relevant → 40-70%
    - Weak match → <30%
    
    Args:
        score: Relevance score between 0 and 1.
    
    Returns:
        Percentage between 0 and 100, rounded to 2 decimals.
    """
    if score <= 0:
        return 0.0
    
    # Apply scaling to push top results to 70%+ range
    # Use a power curve to emphasize higher scores
    scaled = score ** 0.85  # Slight compression for lower scores
    
    # Map to 70-95% range for high scores, with natural falloff
    # Top scores (0.7+) map to 70-95%
    # Mid scores (0.3-0.7) map to 40-70%
    # Low scores (<0.3) map to <30%
    
    if scaled >= 0.7:
        # High relevance: 70-95%
        percent = 70.0 + (scaled - 0.7) / 0.3 * 25.0
    elif scaled >= 0.3:
        # Medium relevance: 40-70%
        percent = 40.0 + (scaled - 0.3) / 0.4 * 30.0
    else:
        # Low relevance: 0-40%
        percent = scaled / 0.3 * 40.0
    
    # Ensure we don't exceed 100%
    percent = min(percent, 100.0)
    
    return round(percent, 2)

