# Find python.exe in common locations and run the backend
$pythonPaths = @(
    "C:\Users\Dell\my_awesome_project\env\Scripts\python.exe",
    "C:\Users\Dell\django-react\env\Scripts\python.exe",
    "C:\Users\Dell\PycharmProjects\pythonProject\venv\Scripts\python.exe",
    "C:\Users\Dell\PycharmProjects\djangoProject\venv\Scripts\python.exe",
    "C:\Users\Dell\PycharmProjects\DP1\venv\Scripts\python.exe"
)

$pyExe = $null
foreach ($p in $pythonPaths) {
    if (Test-Path $p) {
        Write-Output "Found Python at: $p"
        $result = & $p -c "import uvicorn; print('uvicorn:ok')" 2>&1
        if ($result -match 'uvicorn:ok') {
            $pyExe = $p
            Write-Output "uvicorn available! Using this Python."
            break
        } else {
            Write-Output "No uvicorn in this env. Trying next..."
        }
    }
}

if (-not $pyExe) {
    Write-Output "Trying system Python..."
    # Try the Windows Store Python
    $storePython = Get-ChildItem "C:\Users\Dell\AppData\Local\Microsoft\WindowsApps" -Filter "python*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($storePython) {
        Write-Output "Store Python: $storePython"
        $pyExe = $storePython
    }
}

if ($pyExe) {
    Write-Output "Starting backend with: $pyExe"
    Set-Location "d:\comp_bias\backend"
    & $pyExe -m uvicorn app:app --port 8000 --reload
} else {
    Write-Output "ERROR: Could not find a Python with uvicorn installed."
    Write-Output "Please run: pip install -r requirements.txt"
}
