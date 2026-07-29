#!/usr/bin/env bash
# Watchdog/resume for the mass re-classify batch.
# Idempotent: does nothing if the batch is already running or already finished.
# Otherwise relaunches retriage_all.py, which RESUMES from the persisted
# checkpoint (retriage_progress.json) using the stable id snapshot
# (retriage_ids.txt) — so no work is lost across shutdowns/reboots.
#
# Install as cron (every 10 min):
#   */10 * * * * /opt/chatita-mail/scripts/retriage_resume.sh
set -euo pipefail

APP=/opt/chatita-mail
IDS="$APP/scripts/retriage_ids.txt"
PROG="$APP/scripts/retriage_progress.json"
LOG="$APP/scripts/retriage.log"

cd "$APP"

# 1) Already running? nothing to do.
if pgrep -f retriage_all.py >/dev/null 2>&1; then
  exit 0
fi

# 2) Already finished? (checkpoint index >= total ids) -> stop watchdog work.
if [[ -f "$IDS" && -f "$PROG" ]]; then
  total=$(wc -l < "$IDS" | tr -d ' ')
  idx=$("$APP/venv/bin/python" -c "import json;print(json.load(open('$PROG')).get('index',0))" 2>/dev/null || echo 0)
  if [[ "${total:-0}" -gt 0 && "${idx:-0}" -ge "${total}" ]]; then
    exit 0
  fi
fi

# 3) Not running and not done -> (re)launch; retriage_all.py resumes from checkpoint.
echo "[resume $(date -u +%FT%TZ)] relaunching retriage_all.py from checkpoint" >> "$LOG"
RETRIAGE_RATE_PER_MIN="${RETRIAGE_RATE_PER_MIN:-250}" \
PYTHONPATH="$APP" \
  nohup "$APP/venv/bin/python" "$APP/scripts/retriage_all.py" >> "$LOG" 2>&1 &
