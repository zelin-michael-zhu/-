#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/.dev-pids"

stop_one() {
  local name="$1"
  local file="$PID_DIR/$name.pid"

  if [[ ! -f "$file" ]]; then
    echo "[ApplyPilot] $name is not running."
    return
  fi

  local pid
  pid="$(cat "$file")"
  if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    echo "[ApplyPilot] Stopped $name."
  else
    echo "[ApplyPilot] $name process was not active."
  fi

  rm -f "$file"
}

stop_one backend
stop_one frontend

echo "[ApplyPilot] MySQL is still running. Stop it with: docker compose down"
