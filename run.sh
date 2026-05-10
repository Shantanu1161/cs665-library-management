#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# Library Management System - one-shot launcher
# CS665 Project 3
#
# Starts the FastAPI backend on port 8000 and the static
# frontend server on port 3000, then opens the app in
# your default browser. Press Ctrl+C once to stop both.
# ──────────────────────────────────────────────────────────────

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# ── 1. Make sure the venv exists; create it if not ──────────
if [ ! -d "venv" ]; then
    echo "[setup] Virtual environment not found. Creating venv..."
    python3 -m venv venv
fi

# ── 2. Activate venv ────────────────────────────────────────
# shellcheck disable=SC1091
source venv/bin/activate

# ── 3. Install / refresh dependencies if needed ─────────────
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "[setup] Installing Python dependencies..."
    pip install -q -r backend/requirements.txt
fi

# ── 4. Pick free ports (fall back if 8000/3000 are taken) ───
BACKEND_PORT=8000
FRONTEND_PORT=3000
while lsof -i ":$BACKEND_PORT" >/dev/null 2>&1; do
    BACKEND_PORT=$((BACKEND_PORT + 1))
done
while lsof -i ":$FRONTEND_PORT" >/dev/null 2>&1; do
    FRONTEND_PORT=$((FRONTEND_PORT + 1))
done

# If the backend port isn't 8000, patch the frontend's API const
# (only for this run; reverts on cleanup, even if script is killed)
ORIGINAL_JS=""
if [ "$BACKEND_PORT" != "8000" ]; then
    ORIGINAL_JS="$(cat frontend/js/app.js)"
    sed -i.bak "s|http://localhost:8000|http://localhost:$BACKEND_PORT|g" frontend/js/app.js
    # Belt-and-suspenders: even if the trap doesn't fire (SIGKILL etc.),
    # restore the file the next time run.sh starts.
    cp frontend/js/app.js.bak frontend/js/app.js.original-backup 2>/dev/null || true
fi
# If a previous run left a backup behind without restoring, restore it now.
if [ -f frontend/js/app.js.original-backup ] && [ "$BACKEND_PORT" = "8000" ]; then
    mv frontend/js/app.js.original-backup frontend/js/app.js
    rm -f frontend/js/app.js.bak
fi

# ── 5. Start backend (background) ───────────────────────────
echo ""
echo "[backend]  starting on http://localhost:$BACKEND_PORT"
cd backend
uvicorn main:app --port "$BACKEND_PORT" --log-level warning &
BACKEND_PID=$!
cd ..

# ── 6. Start frontend (background) ──────────────────────────
echo "[frontend] starting on http://localhost:$FRONTEND_PORT"
cd frontend
python3 -m http.server "$FRONTEND_PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# ── 7. Cleanup on Ctrl+C ────────────────────────────────────
cleanup() {
    echo ""
    echo "[stop] shutting down..."
    kill "$BACKEND_PID"  2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    if [ -n "$ORIGINAL_JS" ]; then
        printf '%s' "$ORIGINAL_JS" > frontend/js/app.js
        rm -f frontend/js/app.js.bak
    fi
    echo "[stop] done."
    exit 0
}
trap cleanup INT TERM

# ── 8. Wait a couple of seconds, then open the browser ──────
sleep 2
URL="http://localhost:$FRONTEND_PORT"
echo ""
echo "════════════════════════════════════════════════════════"
echo "  App is running:   $URL"
echo "  API docs:         http://localhost:$BACKEND_PORT/docs"
echo "  Press Ctrl+C in this window to stop both servers."
echo "════════════════════════════════════════════════════════"
echo ""

if command -v open >/dev/null 2>&1; then
    open "$URL"             # macOS
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL"         # Linux
fi

# ── 9. Keep script alive until Ctrl+C ───────────────────────
wait
