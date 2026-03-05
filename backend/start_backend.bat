@echo off
set TEMP=D:\tmp_pip
set TMP=D:\tmp_pip
cd /d "d:\comp_bias\backend"
"D:\comp_venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --reload
