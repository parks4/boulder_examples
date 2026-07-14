#!/usr/bin/env bash
# Regenerate all catalog screenshots (docs/_static/screenshots/*.png).
#
# Must be run against a clean `boulder` install with NO third-party plugin on
# the same Python path -- a plugin can override branding/behavior (see
# AGENTS.md's "Custom plugins" section), and screenshots must show plain
# Boulder. Point BOULDER_PYTHON at a venv/conda env's python that has
# `boulder` (matching requirements.txt) installed and nothing else with a
# `boulder.plugins` entry point.
#
# Usage:
#   BOULDER_PYTHON=/path/to/clean/venv/bin/python scripts/capture_all_screenshots.sh
set -e
cd "$(dirname "$0")/.."

VENV_PY="${BOULDER_PYTHON:?Set BOULDER_PYTHON to a clean venv/conda python (no third-party plugins installed)}"
OUT_DIR="docs/_static/screenshots"
PORT="${BOULDER_SCREENSHOT_PORT:-8061}"

EXAMPLES="combustor reactor2 nanosecond_pulse_discharge mix1 reactor1 periodic_cstr fuel_injection continuous_reactor"

kill_port() {
  # bash's `&`/$! PID does not reliably map to the real Windows python.exe
  # PID under git-bash/MSYS, so find it via the port it's actually bound to.
  local port="$1"
  local pid
  pid=$(netstat -ano | grep "LISTENING" | grep ":${port} " | awk '{print $NF}' | head -1)
  if [ -n "$pid" ]; then
    taskkill //PID "$pid" //F > /dev/null 2>&1 || true
  fi
}

# Clear any stale listener before starting (e.g. a prior failed run).
kill_port "$PORT"
sleep 1

for ex in $EXAMPLES; do
  echo "=== $ex ==="
  "$VENV_PY" -m boulder.cli "examples/${ex}.yaml" --no-open --host 0.0.0.0 --port "$PORT" > "/tmp/${ex}_server.log" 2>&1 &
  for i in $(seq 1 20); do
    if curl -sS -o /dev/null "http://localhost:${PORT}" --max-time 2 2>/dev/null; then
      break
    fi
    sleep 1
  done
  sleep 2
  python scripts/capture_screenshot.py "http://localhost:${PORT}" "${OUT_DIR}/${ex}.png" || echo "FAILED: $ex"
  kill_port "$PORT"
  sleep 1
done
echo "done"
