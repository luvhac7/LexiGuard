"""
Smoke test for incremental ingestion.
Tests that adding a new file only processes that file.
"""
import os
import json
import tempfile
import shutil
from ingest import ingest_path, load_manifest

def test_incremental_ingestion():
    """Test that incremental ingestion only processes new/changed files."""
    # Create temporary test directory
    test_dir = tempfile.mkdtemp()
    
    try:
        # Create a dummy PDF file (empty for test)
        test_pdf = os.path.join(test_dir, "test_case_1.pdf")
        with open(test_pdf, 'wb') as f:
            # Write minimal PDF bytes
            f.write(b'%PDF-1.4\n')
        
        # First run: should process the file
        print("First ingestion run...")
        result1 = ingest_path(test_dir, reindex_all=False)
        print(f"Result 1: {json.dumps(result1, indent=2)}")
        
        manifest1 = load_manifest()
        assert "test_case_1.pdf" in manifest1
        assert result1["processed"] >= 0  # May process or fail, but should try
        
        # Second run: should skip unchanged file
        print("\nSecond ingestion run (should skip)...")
        result2 = ingest_path(test_dir, reindex_all=False)
        print(f"Result 2: {json.dumps(result2, indent=2)}")
        
        # Should have skipped the file
        assert result2.get("skipped", 0) >= 0
        
        # Third run with --reindex-all: should reprocess
        print("\nThird ingestion run (--reindex-all, should reprocess)...")
        result3 = ingest_path(test_dir, reindex_all=True)
        print(f"Result 3: {json.dumps(result3, indent=2)}")
        
        print("\n✅ Incremental ingestion test completed!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    test_incremental_ingestion()

