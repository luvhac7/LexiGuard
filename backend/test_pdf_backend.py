"""
Test script to directly test PDF processing backend without frontend.
This will test chunking, Gemini API calls, and responses.
"""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from case_comparer import (
    extract_text_from_pdf,
    clean_pages,
    chunk_text_by_pages,
    summarize_chunk,
    aggregate_case,
    process_case,
    compare_two_cases,
    compare_two_cases_with_file_upload,
    call_gemini
)

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_pdf_backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def test_single_pdf(pdf_path: str, case_name: str = "Case"):
    """Test processing a single PDF with detailed logging."""
    logger.info("=" * 80)
    logger.info(f"Testing {case_name}: {pdf_path}")
    logger.info("=" * 80)
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return None
    
    # Read PDF file
    logger.info(f"Reading PDF file: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
    
    logger.info(f"PDF file size: {len(file_bytes)} bytes")
    
    try:
        # Step 1: Extract pages
        logger.info("\n" + "="*80)
        logger.info("STEP 1: Extracting text from PDF pages")
        logger.info("="*80)
        pages = extract_text_from_pdf(file_bytes)
        logger.info(f"✓ Extracted {len(pages)} pages")
        for i, page in enumerate(pages[:3], 1):  # Show first 3 pages preview
            preview = page[:200].replace('\n', ' ')
            logger.info(f"  Page {i} preview: {preview}...")
        
        if not pages:
            logger.error("No pages extracted!")
            return None
        
        # Step 2: Clean pages
        logger.info("\n" + "="*80)
        logger.info("STEP 2: Cleaning pages")
        logger.info("="*80)
        cleaned_text = clean_pages(pages)
        logger.info(f"✓ Cleaned text length: {len(cleaned_text)} characters")
        logger.info(f"  Preview: {cleaned_text[:300]}...")
        
        # Step 3: Chunk text
        logger.info("\n" + "="*80)
        logger.info("STEP 3: Chunking text")
        logger.info("="*80)
        chunks = chunk_text_by_pages(pages, max_chars=30000, overlap_chars=300)
        logger.info(f"✓ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            logger.info(f"  Chunk {i+1}: {chunk['char_count']} chars, pages {chunk['pages']}")
        
        if not chunks:
            logger.error("No chunks created!")
            return None
        
        # Step 4: Process chunks with Gemini (with detailed logging)
        logger.info("\n" + "="*80)
        logger.info("STEP 4: Summarizing chunks with Gemini")
        logger.info("="*80)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"\n--- Processing Chunk {i+1}/{len(chunks)} ---")
            logger.info(f"Chunk size: {len(chunk['text'])} characters")
            logger.info(f"Chunk pages: {chunk['pages']}")
            logger.info(f"Chunk preview: {chunk['text'][:200]}...")
            
            try:
                chunk_text = chunk["text"][:30000]  # Safety limit
                logger.info(f"Calling Gemini API for chunk {i+1}...")
                
                summary = summarize_chunk(chunk_text)
                
                logger.info(f"✓ Gemini response received for chunk {i+1}")
                logger.info(f"  Response keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
                
                if isinstance(summary, dict):
                    if "error" in summary:
                        logger.warning(f"  ⚠ Chunk {i+1} has error: {summary.get('error')}")
                    else:
                        logger.info(f"  - chunk_excerpt: {summary.get('chunk_excerpt', 'N/A')[:100]}...")
                        logger.info(f"  - background items: {len(summary.get('background', []))}")
                        logger.info(f"  - issues: {len(summary.get('issues', []))}")
                        logger.info(f"  - statutes: {len(summary.get('statutes', []))}")
                        logger.info(f"  - arguments: {len(summary.get('arguments', []))}")
                
                # Validate and add metadata
                if not isinstance(summary, dict) or "error" in summary:
                    logger.warning(f"  Using fallback summary for chunk {i+1}")
                    summary = {
                        "chunk_excerpt": chunk_text[:120],
                        "background": [],
                        "issues": [],
                        "statutes": [],
                        "arguments": [],
                        "analysis_points": [],
                        "decision_clues": []
                    }
                
                summary["chunk_index"] = i
                summary["pages"] = chunk["pages"]
                chunk_summaries.append(summary)
                logger.info(f"✓ Chunk {i+1} summarized successfully")
                
            except Exception as e:
                logger.error(f"✗ Error summarizing chunk {i+1}: {e}", exc_info=True)
                chunk_summaries.append({
                    "chunk_excerpt": chunk["text"][:120],
                    "background": [],
                    "issues": [],
                    "statutes": [],
                    "arguments": [],
                    "analysis_points": [],
                    "decision_clues": [],
                    "chunk_index": i,
                    "pages": chunk["pages"]
                })
        
        if not chunk_summaries:
            logger.error("No chunk summaries created!")
            return None
        
        logger.info(f"\n✓ All {len(chunk_summaries)} chunks summarized")
        
        # Step 5: Aggregate case summary
        logger.info("\n" + "="*80)
        logger.info("STEP 5: Aggregating case summary with Gemini")
        logger.info("="*80)
        logger.info(f"Calling Gemini API to aggregate {len(chunk_summaries)} chunk summaries...")
        
        case_summary = aggregate_case(chunk_summaries)
        
        logger.info(f"✓ Case summary received")
        logger.info(f"  Summary keys: {list(case_summary.keys()) if isinstance(case_summary, dict) else 'Not a dict'}")
        
        if isinstance(case_summary, dict) and "error" in case_summary:
            logger.error(f"  ✗ Error in case summary: {case_summary.get('error')}")
        else:
            logger.info(f"  - case_title: {case_summary.get('case_title', 'N/A')}")
            logger.info(f"  - court: {case_summary.get('court', 'N/A')}")
            logger.info(f"  - date: {case_summary.get('date', 'N/A')}")
        
        case_summary["total_chunks"] = len(chunks)
        case_summary["total_pages"] = len(pages)
        
        return {
            "pages_extracted": len(pages),
            "chunks_created": len(chunks),
            "chunk_summaries_count": len(chunk_summaries),
            "case_summary": case_summary
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        return None


def test_compare_pdfs(pdf_a_path: str, pdf_b_path: str):
    """Test comparing two PDFs."""
    logger.info("\n" + "="*80)
    logger.info("TESTING FULL COMPARISON PIPELINE")
    logger.info("="*80)
    
    logger.info(f"Case A: {pdf_a_path}")
    logger.info(f"Case B: {pdf_b_path}")
    
    # Read PDF files
    logger.info("\nReading PDF files...")
    with open(pdf_a_path, 'rb') as f:
        file_a_bytes = f.read()
    with open(pdf_b_path, 'rb') as f:
        file_b_bytes = f.read()
    
    logger.info(f"Case A size: {len(file_a_bytes)} bytes")
    logger.info(f"Case B size: {len(file_b_bytes)} bytes")
    
    try:
        logger.info("\n" + "="*80)
        logger.info("Calling compare_two_cases function (with file upload method)...")
        logger.info("="*80)
        
        # Try file upload method first
        try:
            logger.info("Attempting file upload method...")
            result = compare_two_cases_with_file_upload(file_a_bytes, file_b_bytes)
        except Exception as e:
            logger.warning(f"File upload method failed: {e}. Using fallback method...")
            result = compare_two_cases(file_a_bytes, file_b_bytes)
        
        logger.info("\n" + "="*80)
        logger.info("COMPARISON COMPLETE!")
        logger.info("="*80)
        logger.info(f"Result keys: {list(result.keys())}")
        
        if "caseA" in result:
            logger.info(f"\nCase A summary keys: {list(result['caseA'].keys()) if isinstance(result['caseA'], dict) else 'N/A'}")
        if "caseB" in result:
            logger.info(f"Case B summary keys: {list(result['caseB'].keys()) if isinstance(result['caseB'], dict) else 'N/A'}")
        if "comparison" in result:
            logger.info(f"Comparison keys: {list(result['comparison'].keys()) if isinstance(result['comparison'], dict) else 'N/A'}")
        
        # Save result to file
        output_file = f"comparison_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✓ Full result saved to: {output_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error comparing PDFs: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # PDF file paths
    pdf_a = r"D:\highcourt_2024\Sangam_Milk_Producer_Company_Ltd_vs_The_Agricultural_Market_Committee_on_5_March_2024.PDF"
    pdf_b = r"D:\highcourt_2024\Randeep_Singh_Rana_vs_The_State_Of_Haryana_on_22_November_2024.PDF"
    
    logger.info("Starting PDF Backend Test")
    logger.info(f"Timestamp: {datetime.now()}")
    
    # Test individual PDFs first
    logger.info("\n" + "#"*80)
    logger.info("TESTING INDIVIDUAL PDF PROCESSING")
    logger.info("#"*80)
    
    result_a = test_single_pdf(pdf_a, "Case A")
    result_b = test_single_pdf(pdf_b, "Case B")
    
    # Test full comparison
    logger.info("\n" + "#"*80)
    logger.info("TESTING FULL COMPARISON")
    logger.info("#"*80)
    
    comparison_result = test_compare_pdfs(pdf_a, pdf_b)
    
    logger.info("\n" + "="*80)
    logger.info("ALL TESTS COMPLETE")
    logger.info("="*80)
    logger.info(f"Check 'test_pdf_backend.log' for detailed logs")

