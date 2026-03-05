import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CHROMA_PATH = os.getenv('CHROMA_PATH') or os.path.join(os.path.dirname(__file__), 'chroma_db')
COLLECTION_NAME = 'legal_cases'


def get_collection():
    """Get or create persistent ChromaDB collection."""
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
    try:
        col = client.get_collection(COLLECTION_NAME)
    except Exception:
        col = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return col


def delete_chunks_by_file_hash(file_hash: str):
    """Delete all chunks matching a file_hash before re-indexing."""
    try:
        col = get_collection()
        # Query to find matching chunks
        results = col.get(
            where={"file_hash": file_hash},
            include=['metadatas']
        )
        if results['ids']:
            col.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} existing chunks for file_hash {file_hash[:8]}...")
    except Exception as e:
        logger.warning(f"Could not delete existing chunks: {e}")


def batch_upsert(chunks: List[Dict[str, Any]], batch_size: int = 500):
    """
    Batch upsert chunks to ChromaDB.
    Default batch_size=500 as specified.
    """
    if not chunks:
        return
    
    col = get_collection()
    
    # Process in batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        ids = [c['id'] for c in batch]
        docs = [c['document'] for c in batch]
        metas = [c['metadata'] for c in batch]
        embs = [c['embedding'] for c in batch]
        
        try:
            col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embs)
            logger.debug(f"Upserted batch {i//batch_size + 1}: {len(batch)} chunks")
        except Exception as e:
            logger.error(f"Error upserting batch: {e}")
            raise
