"""
Simple script to ingest D:\high_court_2025 into ChromaDB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest import ingest_path

if __name__ == "__main__":
    print("Starting ingestion of D:\\high_court_2025...")
    result = ingest_path("D:\\high_court_2025", reindex_all=False)
    print("\n" + "="*60)
    print("INGESTION SUMMARY:")
    print("="*60)
    print(f"Processed: {result.get('processed', 0)} files")
    print(f"Skipped: {result.get('skipped', 0)} files")
    print(f"Errors: {result.get('errors', 0)} files")
    print(f"Total Chunks: {result.get('total_chunks', 0)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print("="*60)

