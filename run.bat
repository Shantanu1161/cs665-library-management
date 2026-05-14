@echo off
REM ──────────────────────────────────────────────────────────────
REM Library Management System - one-shot launcher (Windows)
REM CS665 Project 3
REM
REM Why the explicit venv\Scripts\python.exe path is used everywhere
REM below: when a user has multiple Pythons on PATH (Anaconda, the
REM Microsoft Store python, pyenv, etc.), an `activate.bat` call
REM does not always win. Calling the venv's python.exe directly is
REM the only reliable way to guarantee fastapi installs into the
REM same interpreter that later runs main.py.
REM ──────────────────────────────────────────────────────────────

cd /d "%~dp0"

REM ── 1. Verify Python is installed ──
where python >nul 2>nul
if errorlevel 1 (
    echo [error] Python is not installed or not on PATH.
    echo         Install Python 3.10+ from https://python.org and re-run.
    pause
    exit /b 1
)

REM ── 2. Create venv if missing ──
if not exist venv (
    echo [setup] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [error] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM ── 3. Use the venv's python.exe directly for everything below ──
set "VENV_PY=%~dp0venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [error] venv\Scripts\python.exe not found.
    echo         Delete the venv folder and re-run this script.
    pause
    exit /b 1
)

REM ── 4. Upgrade pip and install dependencies (always run, idempotent) ──
echo [setup] Installing/verifying Python dependencies...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>nul
"%VENV_PY%" -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo [error] pip install failed. Check the output above for the cause.
    pause
    exit /b 1
)

REM ── 5. Verify the install actually worked ──
"%VENV_PY%" -c "import fastapi, uvicorn, pydantic" 2>nul
if errorlevel 1 (
    echo [error] fastapi/uvicorn/pydantic could not be imported even after install.
    echo         Run "%VENV_PY%" -m pip install -r backend\requirements.txt by hand
    echo         and read the output.
    pause
    exit /b 1
)
echo [setup] Dependencies OK.
echo.

REM ── 6. Start backend in a new window (using venv python directly) ──
start "Library Backend" cmd /k ""%VENV_PY%" "%~dp0backend\main.py""

REM ── 7. Start frontend in a new window (using venv python directly) ──
start "Library Frontend" cmd /k "cd /d "%~dp0frontend" && "%VENV_PY%" -m http.server 3000"

REM ── 8. Wait a moment, then open the browser ──
timeout /t 4 /nobreak >nul
start "" http://localhost:3000

echo.
echo ════════════════════════════════════════════════════════
echo   App running at:  http://localhost:3000
echo   API docs:        http://localhost:8000/docs
echo   Close the two terminal windows that opened to stop.
echo ════════════════════════════════════════════════════════
echo.
pause
