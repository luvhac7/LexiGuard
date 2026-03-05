import argparse
import json
import logging
import os
import shutil
from typing import List, Dict, Any

from utils import (
    load_manifest, save_manifest, append_ingest_report,
    sha256_file, sha256_text, utc_now_iso, timeit
)
from extractor import extract_pdf_pages, write_raw_text
from cleaner import clean_pages_to_file
from chunker import split_text_recursive
from embedder import SentenceEmbedder
from chroma_client import batch_upsert, delete_chunks_by_file_hash

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, 'ingest_report.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

FAILED_DIR = os.path.join(os.path.dirname(__file__), 'failed')
os.makedirs(FAILED_DIR, exist_ok=True)

# Toggle moving files to failed folder
MOVE_FAILED = os.getenv('MOVE_FAILED', 'false').lower() == 'true'


def find_pdfs_recursive(path: str) -> List[str]:
    """Recursively find all PDF files in directory."""
    pdf_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """Extract case title, date, year from filename if possible."""
    base = os.path.splitext(filename)[0]
    # Try to extract date patterns like "on_6_May_2025"
    date_match = None
    year = None
    
    # Look for date patterns
    import re
    date_patterns = [
        r'on_(\d+)_(\w+)_(\d{4})',  # on_6_May_2025
        r'(\d{4})',  # Just year
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, base)
        if match:
            if len(match.groups()) == 3:
                # Extract full date
                date_match = match.group(0).replace('_', ' ')
                year = int(match.groups()[2])
            elif len(match.groups()) == 1:
                try:
                    year = int(match.groups()[0])
                except Exception:
                    year = None
            break
    
    case_title = base.replace('_', ' ').replace(' on ', ' ').title()
    
    return {
        "case_title": case_title,
        "date": date_match or "",
        "year": year if isinstance(year, int) else -1
    }


def sanitize_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure no None values exist; replace with safe defaults."""
    safe = {}
    for k, v in meta.items():
        if v is None:
            safe[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            safe[k] = v
        else:
            # Fallback to string repr
            safe[k] = str(v)
    return safe


def process_pdf(
    pdf_path: str,
    reindex_all: bool,
    embedder: SentenceEmbedder,
    manifest: Dict[str, Any],
    dedupe_text_hashes: set
) -> Dict[str, Any]:
    """Process a single PDF: extract, clean, chunk, embed, store."""
    filename = os.path.basename(pdf_path)
    file_hash = sha256_file(pdf_path)
    
    entry = manifest.get(filename)
    if entry and not reindex_all and entry.get('sha256') == file_hash:
        logger.info(f"SKIPPED: {filename} (unchanged)")
        return {"file": filename, "status": "skipped"}
    
    # If file hash changed, delete old chunks
    if entry and entry.get('sha256') != file_hash:
        logger.info(f"REPROCESSING: {filename} (hash changed)")
        delete_chunks_by_file_hash(entry.get('sha256'))
    
    logger.info(f"PROCESSING: {filename}")
    start, end = timeit()
    
    try:
        # Extract
        pages = extract_pdf_pages(pdf_path)
        write_raw_text(filename, pages)
        clean_path = clean_pages_to_file(filename, pages)
        
        with open(clean_path, 'r', encoding='utf-8') as f:
            cleaned = f.read()
        
        # Chunk
        chunks = split_text_recursive(cleaned, chunk_size=3000, chunk_overlap=600)
        
        # Deduplication: within file
        seen_hashes = set()
        unique_chunks = []
        text_hashes = []
        
        for chunk in chunks:
            text_hash = sha256_text(chunk)
            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_chunks.append(chunk)
                text_hashes.append(text_hash)
            else:
                logger.debug(f"Deduplicated duplicate chunk in {filename}")
        
        if not unique_chunks:
            logger.warning(f"No unique chunks after deduplication for {filename}")
            return {"file": filename, "status": "error", "error": "No unique chunks"}
        
        # Extract metadata
        base_meta = extract_metadata_from_filename(filename)
        
        # Build records for Chroma
        records: List[Dict[str, Any]] = []
        base_id = os.path.splitext(filename)[0].replace('/', '_').replace('\\', '_')
        
        for idx, (chunk, text_hash) in enumerate(zip(unique_chunks, text_hashes)):
            meta = {
                "case_title": base_meta.get("case_title"),
                "court": "High Court",
                "year": base_meta.get("year"),
                "date": base_meta.get("date"),
                "source_path": pdf_path,
                "chunk_idx": idx,
                "page_range": "",
                "file_hash": file_hash,
                "text_hash": text_hash,
            }
            meta = sanitize_metadata(meta)
            
            rec = {
                "id": f"HighCourt_{base_id}_chunk_{idx:03d}",
                "document": chunk,
                "metadata": meta,
            }
            records.append(rec)
        
        # Embed
        logger.info(f"Embedding {len(records)} chunks for {filename}")
        embeddings = embedder.encode([r['document'] for r in records])
        for r, e in zip(records, embeddings):
            r['embedding'] = e
        
        # Batch upsert
        batch_size = int(os.getenv('CHROMA_BATCH_SIZE', '500'))
        for i in range(0, len(records), batch_size):
            batch_upsert(records[i:i+batch_size], batch_size=batch_size)
        
        # Update manifest
        manifest[filename] = {
            "sha256": file_hash,
            "last_indexed_at": utc_now_iso(),
            "num_chunks": len(records)
        }
        
        duration = f"{end():.1f}s"
        logger.info(f"INDEXED: {filename} - {len(records)} chunks in {duration}")
        
        report_entry = {
            "file": filename,
            "status": "indexed",
            "chunks": len(records),
            "sha256": file_hash,
            "duration": duration,
            "first_chunk_excerpt": (records[0]['document'][:120] if records else "")
        }
        append_ingest_report(report_entry)
        return report_entry
        
    except Exception as e:
        logger.error(f"ERROR processing {filename}: {str(e)}", exc_info=True)
        
        # Optionally move to failed directory
        if MOVE_FAILED:
            try:
                fail_target = os.path.join(FAILED_DIR, filename)
                if os.path.exists(pdf_path):
                    try:
                        shutil.move(pdf_path, fail_target)
                    except Exception as move_err:
                        logger.warning(f"Could not move file to failed/: {move_err}")
            except Exception:
                pass
        
        append_ingest_report({"file": filename, "status": "error", "error": str(e)})
        return {"file": filename, "status": "error", "error": str(e)}


def verify_ingestion(filename: str, sample_query: str = None) -> bool:
    """QA verification: query ChromaDB to verify chunks are retrievable."""
    try:
        from chroma_client import get_collection
        
        col = get_collection()
        if sample_query is None:
            # Use a generic query
            sample_query = "Section"
        
        # Query top-K=5
        results = col.query(
            query_texts=[sample_query],
            n_results=5
        )
        
        if results['ids'] and len(results['ids'][0]) > 0:
            logger.info(f"QA VERIFIED: {filename} - Found {len(results['ids'][0])} results for query")
            return True
        else:
            logger.warning(f"QA WARNING: {filename} - No results found for query")
            return False
    except Exception as e:
        logger.warning(f"QA verification failed: {e}")
        return False


def ingest_path(path: str, reindex_all: bool = False, max_files: int | None = None) -> Dict[str, Any]:
    """Main ingestion orchestration."""
    manifest = load_manifest()
    embedder = SentenceEmbedder()
    
    # Recursive PDF finding
    pdf_files = find_pdfs_recursive(path)
    logger.info(f"Found {len(pdf_files)} PDF files to process")

    # Limit number of files if requested
    if max_files is not None:
        pdf_files = pdf_files[:max_files]
    
    if not pdf_files:
        return {
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "total_chunks": 0,
            "status": "no_files_found"
        }
    
    processed = 0
    skipped = 0
    errors = 0
    total_chunks = 0
    
    # Track text hashes for cross-file deduplication (optional, currently disabled)
    dedupe_text_hashes = set()
    
    for pdf in pdf_files:
        # Skip if file no longer exists
        if not os.path.exists(pdf):
            logger.warning(f"Missing file, skipping: {pdf}")
            errors += 1
            continue
        
        result = process_pdf(pdf, reindex_all, embedder, manifest, dedupe_text_hashes)
        
        if result.get('status') == 'indexed':
            processed += 1
            total_chunks += result.get('chunks', 0)
        elif result.get('status') == 'skipped':
            skipped += 1
        else:
            errors += 1
        
        save_manifest(manifest)
    
    status = "completed" if errors == 0 else ("completed_with_errors" if processed > 0 else "failed")
    
    summary = {
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
        "total_chunks": total_chunks,
        "status": status,
    }
    
    logger.info(f"INGESTION COMPLETE: {json.dumps(summary, indent=2)}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Ingest legal PDFs into ChromaDB")
    parser.add_argument('--path', required=True, help='Directory containing PDFs (recursive)')
    parser.add_argument('--reindex-all', action='store_true', help='Rebuild all embeddings')
    parser.add_argument('--max-files', type=int, default=None, help='Limit number of PDFs to process')
    parser.add_argument('--no-move-failed', action='store_true', help='Do not move errored PDFs to failed directory')
    args = parser.parse_args()
    
    # Set MOVE_FAILED flag based on CLI
    global MOVE_FAILED
    if args.no_move_failed:
        MOVE_FAILED = False
    
    result = ingest_path(args.path, reindex_all=args.reindex_all, max_files=args.max_files)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
