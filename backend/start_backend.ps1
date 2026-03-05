# Backend Start Script — uses D:\comp_venv (Python 3.12)
# NOTE: C drive is full, so TEMP/TMP must point to D drive

$env:TEMP = "D:\tmp_pip"
$env:TMP = "D:\tmp_pip"

Set-Location "d:\comp_bias\backend"
& "D:\comp_venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --reload
