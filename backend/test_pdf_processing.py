"""
Test script to test PDF processing, chunking, and Gemini calls without frontend.
Tests the two PDF files provided by the user.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv()
load_dotenv(project_root / '.env')
load_dotenv(project_root / 'api_testing' / '.env')

from case_comparer import (
    extract_text_from_pdf,
    clean_pages,
    chunk_text_by_pages,
    summarize_chunk,
    aggregate_case,
    process_case,
    compare_two_cases
)

# PDF file paths
PDF_A = r"D:\highcourt_2024\Sangam_Milk_Producer_Company_Ltd_vs_The_Agricultural_Market_Committee_on_5_March_2024.PDF"
PDF_B = r"D:\highcourt_2024\Randeep_Singh_Rana_vs_The_State_Of_Haryana_on_22_November_2024.PDF"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_single_pdf(pdf_path, pdf_name):
    """Test processing a single PDF."""
    print_section(f"TESTING: {pdf_name}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        return None
    
    file_size = os.path.getsize(pdf_path)
    print(f"📄 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    # Step 1: Read PDF bytes
    print("\n[1] Reading PDF file...")
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        print(f"✅ Read {len(pdf_bytes):,} bytes")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None
    
    # Step 2: Extract text from PDF
    print("\n[2] Extracting text from PDF...")
    start_time = time.time()
    try:
        pages = extract_text_from_pdf(pdf_bytes)
        elapsed = time.time() - start_time
        print(f"✅ Extracted {len(pages)} pages in {elapsed:.2f} seconds")
        
        # Show page statistics
        total_chars = sum(len(p) for p in pages)
        print(f"   Total characters: {total_chars:,}")
        print(f"   Average chars per page: {total_chars // len(pages) if pages else 0:,}")
        
        # Show first 200 chars of first page
        if pages and len(pages[0]) > 0:
            preview = pages[0][:200].replace('\n', ' ')
            print(f"   First page preview: {preview}...")
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 3: Clean pages
    print("\n[3] Cleaning pages (removing headers/footers)...")
    start_time = time.time()
    try:
        cleaned_text = clean_pages(pages)
        elapsed = time.time() - start_time
        print(f"✅ Cleaned text: {len(cleaned_text):,} characters in {elapsed:.2f} seconds")
        print(f"   Reduction: {len(''.join(pages)) - len(cleaned_text):,} chars removed")
    except Exception as e:
        print(f"❌ Error cleaning pages: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 4: Chunk text
    print("\n[4] Chunking text...")
    start_time = time.time()
    try:
        chunks = chunk_text_by_pages(pages, max_chars=30000, overlap_chars=300)
        elapsed = time.time() - start_time
        print(f"✅ Created {len(chunks)} chunks in {elapsed:.2f} seconds")
        
        # Show chunk details
        for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
            print(f"   Chunk {i+1}: {chunk['char_count']:,} chars, pages {min(chunk['pages'])+1}-{max(chunk['pages'])+1}")
        if len(chunks) > 5:
            print(f"   ... and {len(chunks) - 5} more chunks")
    except Exception as e:
        print(f"❌ Error chunking: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 5: Test Gemini API - summarize first chunk
    print("\n[5] Testing Gemini API call (summarizing first chunk)...")
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not set, skipping Gemini test")
        return {
            "pages": len(pages),
            "chunks": len(chunks),
            "total_chars": total_chars
        }
    
    start_time = time.time()
    try:
        first_chunk_text = chunks[0]["text"][:30000]
        print(f"   Chunk text length: {len(first_chunk_text):,} characters")
        print("   Calling Gemini API...")
        
        summary = summarize_chunk(first_chunk_text)
        elapsed = time.time() - start_time
        
        if "error" in summary:
            print(f"❌ Gemini API error: {summary.get('error', 'Unknown error')}")
            print(f"   Response: {json.dumps(summary, indent=2)[:500]}")
        else:
            print(f"✅ Gemini API call successful in {elapsed:.2f} seconds")
            print(f"   Summary keys: {list(summary.keys())}")
            if "chunk_excerpt" in summary:
                print(f"   Excerpt: {summary['chunk_excerpt'][:150]}...")
            if "issues" in summary and summary["issues"]:
                print(f"   Issues found: {len(summary['issues'])}")
                print(f"   First issue: {summary['issues'][0][:100]}...")
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        import traceback
        traceback.print_exc()
        return {
            "pages": len(pages),
            "chunks": len(chunks),
            "total_chars": total_chars,
            "gemini_error": str(e)
        }
    
    return {
        "pages": len(pages),
        "chunks": len(chunks),
        "total_chars": total_chars,
        "gemini_success": True,
        "first_chunk_summary": summary
    }

def test_full_processing(pdf_path, pdf_name):
    """Test full processing pipeline (including all Gemini calls)."""
    print_section(f"FULL PROCESSING TEST: {pdf_name}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        return None
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not set")
        return None
    
    print("⚠️  WARNING: This will make multiple Gemini API calls and may take several minutes...")
    print("   Starting full processing pipeline...\n")
    
    start_time = time.time()
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"📄 Processing {len(pdf_bytes):,} bytes...")
        result = process_case(pdf_bytes)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Full processing completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        print(f"\nResult structure:")
        print(f"   Keys: {list(result.keys())}")
        
        if "case_title" in result:
            print(f"   Case Title: {result.get('case_title')}")
        if "total_chunks" in result:
            print(f"   Total Chunks: {result.get('total_chunks')}")
        if "total_pages" in result:
            print(f"   Total Pages: {result.get('total_pages')}")
        
        # Save result to file
        output_file = f"test_result_{pdf_name.replace('.PDF', '').replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full result saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in full processing: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print_section("PDF PROCESSING TEST - BACKEND ONLY")
    print("Testing PDF extraction, chunking, and Gemini API calls")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
    else:
        print("⚠️  WARNING: GEMINI_API_KEY not found")
    
    # Test PDF A - Basic extraction and chunking
    result_a = test_single_pdf(PDF_A, "PDF A (Sangam Milk)")
    
    print("\n" + "-" * 80 + "\n")
    
    # Test PDF B - Basic extraction and chunking
    result_b = test_single_pdf(PDF_B, "PDF B (Randeep Singh)")
    
    # Optionally test full processing (commented out by default as it takes time)
    # Uncomment to test full pipeline:
    # print("\n" + "=" * 80)
    # print("OPTIONAL: Full processing test (will make many Gemini API calls)")
    # print("=" * 80)
    # response = input("\nRun full processing test? This will take several minutes. (y/n): ")
    # if response.lower() == 'y':
    #     test_full_processing(PDF_A, "Sangam_Milk")
    
    print_section("TEST SUMMARY")
    print(f"PDF A Results: {json.dumps(result_a, indent=2) if result_a else 'Failed'}")
    print(f"\nPDF B Results: {json.dumps(result_b, indent=2) if result_b else 'Failed'}")
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()

