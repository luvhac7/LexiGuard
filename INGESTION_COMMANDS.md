# PDF Ingestion Commands for ChromaDB

## Quick Start Commands

### Method 1: Direct Python Script (Recommended)

```powershell
# Navigate to backend directory
cd "d:\v2 2\backend"

# Run ingestion script
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\high_court_2025"
```

### Method 2: Using the Simple Ingestion Script

```powershell
# Navigate to backend directory
cd "d:\v2 2\backend"

# Run the simple ingestion script
& "D:\v2_venv\Scripts\python.exe" ingest_highcourt.py
```

### Method 3: Re-index All Files (Force Rebuild)

```powershell
cd "d:\v2 2\backend"
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\high_court_2025" --reindex-all
```

### Method 4: Limit Number of Files (Testing)

```powershell
cd "d:\v2 2\backend"
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\high_court_2025" --max-files 10
```

### Method 5: Using API (If Backend Server is Running)

```powershell
# Start backend server first (in another terminal)
cd "d:\v2 2\backend"
& "D:\v2_venv\Scripts\python.exe" -m uvicorn app:app --port 8000

# Then in another terminal, trigger ingestion via API:
curl -X POST http://localhost:8000/api/ingest -H "Content-Type: application/json" -d '{\"path\": \"D:\\high_court_2025\", \"reindex\": false}'

# Check status:
curl http://localhost:8000/api/ingest/status
```

## Command Options

| Option | Description |
|--------|-------------|
| `--path` | **Required.** Directory containing PDFs (will search recursively) |
| `--reindex-all` | Force re-index all files, even if unchanged |
| `--max-files` | Limit number of PDFs to process (useful for testing) |
| `--no-move-failed` | Don't move failed PDFs to failed directory |

## Examples

### Ingest a different directory:
```powershell
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\legal_documents"
```

### Ingest and re-index everything:
```powershell
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\high_court_2025" --reindex-all
```

### Test with first 5 files:
```powershell
& "D:\v2_venv\Scripts\python.exe" ingest.py --path "D:\high_court_2025" --max-files 5
```

## What Happens During Ingestion

1. **Finds PDFs**: Recursively searches the directory for all `.pdf` files
2. **Extracts Text**: Extracts text from each PDF page
3. **Cleans Text**: Removes headers, footers, and boilerplate
4. **Chunks Text**: Splits into chunks of ~3000 characters with 600 char overlap
5. **Creates Embeddings**: Generates vector embeddings for each chunk
6. **Stores in ChromaDB**: Saves embeddings and metadata to vector database
7. **Updates Manifest**: Tracks which files have been processed

## Output Files

- `backend/manifest.json` - Tracks processed files and their SHA256 hashes
- `backend/ingest_report.json` - Detailed ingestion report
- `backend/logs/ingest_report.log` - Log file
- `backend/chroma_db/` - ChromaDB vector database storage
- `backend/processed_texts/` - Cached raw and cleaned text

## Troubleshooting

### Model Loading Issues
If you see model loading errors, the system will automatically try fallback models:
1. `all-MiniLM-L6-v2` (simple, reliable)
2. `sentence-transformers/all-MiniLM-L6-v2`
3. `law-ai/InLegalBERT` (legal-specific)
4. `nlpaueb/legal-bert-base-uncased`

### Check Ingestion Status
```powershell
# View the log file
Get-Content "d:\v2 2\backend\logs\ingest_report.log" -Tail 50

# View the report
Get-Content "d:\v2 2\backend\ingest_report.json"
```

### Check What Files Were Processed
```powershell
# View manifest
Get-Content "d:\v2 2\backend\manifest.json"
```

## Notes

- Ingestion is **incremental** by default - unchanged files are skipped
- Use `--reindex-all` to rebuild embeddings for all files
- Failed files are moved to `backend/failed/` directory (unless `--no-move-failed` is used)
- The process can take time depending on:
  - Number of PDFs
  - Size of PDFs
  - Your system's processing power

