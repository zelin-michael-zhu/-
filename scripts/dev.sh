#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/.dev-logs"
PID_DIR="$ROOT_DIR/.dev-pids"

mkdir -p "$LOG_DIR" "$PID_DIR"

cd "$ROOT_DIR"

echo "[ApplyPilot] Starting MySQL..."
docker compose up -d

echo "[ApplyPilot] Preparing backend..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed_universities
python -m app.scripts.seed_crawl_sources
python -m app.scripts.seed_demo_data

echo "[ApplyPilot] Preparing frontend..."
cd "$ROOT_DIR/frontend"
corepack pnpm install

stop_pid_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file")"
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "$file"
  fi
}

cleanup() {
  stop_pid_file "$PID_DIR/backend.pid"
  stop_pid_file "$PID_DIR/frontend.pid"
}

trap cleanup INT TERM

wait_for_url() {
  local name="$1"
  local url="$2"
  local attempts="${3:-40}"

  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[ApplyPilot] $name is ready: $url"
      return 0
    fi
    sleep 1
  done

  echo "[ApplyPilot] $name did not become ready: $url"
  echo "[ApplyPilot] Check logs in $LOG_DIR"
  return 1
}

echo "[ApplyPilot] Starting backend..."
stop_pid_file "$PID_DIR/backend.pid"
nohup bash -lc "cd '$ROOT_DIR/backend' && source .venv/bin/activate && exec uvicorn main:app --reload --host 127.0.0.1 --port 8000" \
  > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_DIR/backend.pid"

echo "[ApplyPilot] Starting frontend..."
stop_pid_file "$PID_DIR/frontend.pid"
nohup bash -lc "cd '$ROOT_DIR/frontend' && exec corepack pnpm dev --hostname 127.0.0.1 --port 3000" \
  > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PID_DIR/frontend.pid"

wait_for_url "Backend" "http://127.0.0.1:8000/api/health"
wait_for_url "Frontend" "http://127.0.0.1:3000/en"

cat <<EOF

[ApplyPilot] Local dev is running.

Frontend:
  http://localhost:3000/en
  http://localhost:3000/zh
  http://localhost:3000/en/browser-agent

Backend:
  http://localhost:8000/docs
  http://localhost:8000/api/health

Logs:
  $LOG_DIR/backend.log
  $LOG_DIR/frontend.log

Stop:
  ./scripts/stop-dev.sh

EOF

if [[ "${APPLYPILOT_DETACH:-0}" == "1" ]]; then
  echo "[ApplyPilot] Detached mode requested. Servers will continue in the background."
  trap - INT TERM
  exit 0
fi

echo "[ApplyPilot] Press Ctrl+C to stop backend and frontend."
wait "$BACKEND_PID" "$FRONTEND_PID"
