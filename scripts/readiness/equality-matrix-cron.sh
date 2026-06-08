#!/usr/bin/env bash
# equality-matrix-cron.sh — fail-loud weekly machine-equality matrix build (#2972).
#
# Replaces the inline weekly cron chain:
#   collect-equality.sh && uv run python build-equality-matrix.py >> <dated>.log 2>&1
# which (a) lost its pyyaml dep under `uv run python` (ModuleNotFoundError) and
# (b) buried the exit-1 failure in an unread dated log with no alert.
#
# This wrapper: builds via the PEP-723 self-contained `uv run --script` path, and on
# ANY failure emits a JSONL notification (scripts/notify.sh) AND exits non-zero so
# cron status + monitoring see it. JSONL-only per #2967 user decision (Telegram = F4).
set -uo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo "/mnt/local-analysis/workspace-hub")"
cd "$REPO_ROOT" || { echo "equality-matrix-cron: cannot cd to repo root" >&2; exit 1; }

fail() {
  local msg="$1"
  bash "$REPO_ROOT/scripts/notify.sh" cron equality-matrix fail "$msg" || true
  echo "equality-matrix-cron FAIL: $msg" >&2
  exit 1
}

bash "$REPO_ROOT/scripts/readiness/collect-equality.sh" || fail "collect-equality.sh failed"
uv run --script "$REPO_ROOT/scripts/readiness/build-equality-matrix.py" || fail "build-equality-matrix.py failed (deps/build)"
bash "$REPO_ROOT/scripts/notify.sh" cron equality-matrix pass "matrix rebuilt" || true
echo "equality-matrix-cron OK"
