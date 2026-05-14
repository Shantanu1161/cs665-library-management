@echo off
REM ──────────────────────────────────────────────────────────────
REM Library Management System - one-shot launcher (Windows)
REM CS665 Project 3
REM ──────────────────────────────────────────────────────────────

cd /d "%~dp0"

REM ── 1. Create venv if missing ──
if not exist venv (
    echo [setup] Creating virtual environment...
    python -m venv venv
)

REM ── 2. Activate venv ──
call venv\Scripts\activate.bat

REM ── 3. Install deps if missing ──
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [setup] Installing Python dependencies...
    pip install -q -r backend\requirements.txt
)

REM ── 4. Start backend in a new window ──
REM Using `python main.py` instead of `uvicorn main:app --reload` because the
REM colon syntax can break in Windows PowerShell. main.py has an
REM `if __name__ == "__main__": uvicorn.run(...)` block that does the same thing.
start "Library Backend"  cmd /k "call venv\Scripts\activate.bat && cd backend && python main.py"

REM ── 5. Start frontend in a new window ──
start "Library Frontend" cmd /k "cd frontend && python -m http.server 3000"

REM ── 6. Wait a moment, then open the browser ──
timeout /t 3 /nobreak >nul
start "" http://localhost:3000

echo.
echo ════════════════════════════════════════════════════════
echo   App running at:  http://localhost:3000
echo   API docs:        http://localhost:8000/docs
echo   Close the two terminal windows that opened to stop.
echo ════════════════════════════════════════════════════════
echo.
pause
