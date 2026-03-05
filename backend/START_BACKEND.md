# Backend Start Command

## Simple Command (from backend directory):
```powershell
cd "D:\v2 2\backend"
D:\v2_venv\Scripts\python.exe -m uvicorn app:app --port 8000 --reload
```

## One-liner:
```powershell
cd "D:\v2 2\backend"; D:\v2_venv\Scripts\python.exe -m uvicorn app:app --port 8000 --reload
```

## Or use the batch file:
Double-click `start_backend.bat` in the backend folder

## Notes:
- API keys are automatically loaded from `api_testing/.env`
- Backend will run on `http://localhost:8000`
- `--reload` flag enables auto-reload on code changes

