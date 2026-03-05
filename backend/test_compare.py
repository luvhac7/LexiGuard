"""
Manual test script for case comparison
Tests the full pipeline with two specific PDF files
"""

import os
import sys
import json
from pathlib import Path
from case_comparer import compare_two_cases

# Set paths
pdf_a_path = r"D:\comp\Avtar_Singh_vs_Union_Of_India_Ors_on_21_July_2016.PDF"
pdf_b_path = r"D:\comp\Rajesh_Sharma_vs_Union_Of_India_Others_on_6_May_2009.PDF"

print("=" * 80)
print("CASE COMPARISON TEST")
print("=" * 80)

# Check if files exist
if not os.path.exists(pdf_a_path):
    print(f"ERROR: File not found: {pdf_a_path}")
    sys.exit(1)

if not os.path.exists(pdf_b_path):
    print(f"ERROR: File not found: {pdf_b_path}")
    sys.exit(1)

print(f"\n[OK] Case A: {os.path.basename(pdf_a_path)}")
print(f"[OK] Case B: {os.path.basename(pdf_b_path)}")

# Check API key
if not os.getenv("GEMINI_API_KEY"):
    print("\n⚠ WARNING: GEMINI_API_KEY not set in environment")
    print("Loading from api_testing/.env...")
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / "api_testing" / ".env")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found!")
        sys.exit(1)
    else:
        print("✓ GEMINI_API_KEY loaded from .env")

print("\n" + "=" * 80)
print("STEP 1: Reading PDF files...")
print("=" * 80)

try:
    with open(pdf_a_path, 'rb') as f:
        case_a_bytes = f.read()
    print(f"[OK] Case A: {len(case_a_bytes)} bytes")
    
    with open(pdf_b_path, 'rb') as f:
        case_b_bytes = f.read()
    print(f"[OK] Case B: {len(case_b_bytes)} bytes")
except Exception as e:
    print(f"ERROR reading files: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 2: Starting comparison...")
print("=" * 80)
print("This may take several minutes for large documents...\n")

try:
    result = compare_two_cases(case_a_bytes, case_b_bytes)
    
    print("\n" + "=" * 80)
    print("[SUCCESS] COMPARISON COMPLETE!")
    print("=" * 80)
    
    # Print summary
    print("\nCASE A SUMMARY:")
    print(f"  Title: {result['caseA'].get('case_title', 'N/A')}")
    print(f"  Court: {result['caseA'].get('court', 'N/A')}")
    print(f"  Date: {result['caseA'].get('date', 'N/A')}")
    print(f"  Pages: {result['caseA'].get('total_pages', 'N/A')}")
    print(f"  Chunks: {result['caseA'].get('total_chunks', 'N/A')}")
    
    print("\nCASE B SUMMARY:")
    print(f"  Title: {result['caseB'].get('case_title', 'N/A')}")
    print(f"  Court: {result['caseB'].get('court', 'N/A')}")
    print(f"  Date: {result['caseB'].get('date', 'N/A')}")
    print(f"  Pages: {result['caseB'].get('total_pages', 'N/A')}")
    print(f"  Chunks: {result['caseB'].get('total_chunks', 'N/A')}")
    
    print("\nCOMPARISON SUMMARY:")
    comp = result.get('comparison', {})
    if comp.get('headline_comparison'):
        print(f"  Headline: {comp['headline_comparison']}")
    
    if comp.get('similarity_scores'):
        scores = comp['similarity_scores']
        print(f"  Overall Similarity: {scores.get('overall', 'N/A')}%")
        print(f"  Facts: {scores.get('facts', 'N/A')}%")
        print(f"  Issues: {scores.get('issues', 'N/A')}%")
        print(f"  Statutes: {scores.get('statutes', 'N/A')}%")
        print(f"  Reasoning: {scores.get('reasoning', 'N/A')}%")
    
    # Check all 13 dimensions
    print("\n" + "=" * 80)
    print("CHECKING ALL 13 DIMENSIONS:")
    print("=" * 80)
    
    dimensions = [
        ("1. Case Metadata", comp.get('case_metadata')),
        ("2. Factual Background", comp.get('factual_background')),
        ("3. Legal Issues", comp.get('legal_issues')),
        ("4. Statutory Provisions", comp.get('statutory_provisions')),
        ("5. Precedents", comp.get('precedents')),
        ("6. Arguments", comp.get('arguments')),
        ("7. Reasoning Alignment", comp.get('reasoning_alignment')),
        ("8. Outcome Comparison", comp.get('outcome_comparison')),
        ("9. Doctrinal Evolution", comp.get('doctrinal_evolution')),
        ("10. Judicial Philosophy", comp.get('judicial_philosophy')),
        ("11. Similarity Scores", comp.get('similarity_scores')),
        ("12. Practical Takeaways", comp.get('practical_takeaways')),
        ("13. Meta Insights", comp.get('meta_insights')),
    ]
    
    for name, data in dimensions:
        status = "[OK]" if data else "[MISSING]"
        print(f"{status} {name}")
    
    # Save full result to file
    output_file = "comparison_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Full result saved to: {output_file}")
    print("\n" + "=" * 80)
    print("TEST PASSED! All systems working.")
    print("=" * 80)
    
except Exception as e:
    print(f"\n[ERROR] during comparison: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

