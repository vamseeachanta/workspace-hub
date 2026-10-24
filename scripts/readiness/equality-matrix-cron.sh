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
# Publish evidence + render to origin/main via a sparse worktree. The matrix only
# compares machines equally when every box's evidence reaches origin; the old
# delegation to repo-sync went dark whenever the interactive checkout diverged
# (non-FF pile-up) or the sync cron died.
publish_start=$(date -u +%Y-%m-%dT%H:%M:%SZ) || fail "cannot timestamp publication start"
bash "$REPO_ROOT/scripts/readiness/publish-equality.sh" --rebuild \
  || fail "publish-equality.sh failed (evidence not on origin)"
# A successful exit alone is insufficient: require this invocation's publication record.
# shellcheck source=scripts/readiness/lib/eq-seam.sh
. "$REPO_ROOT/scripts/readiness/lib/eq-seam.sh"
health_file="$(eq_state_dir "")/publish-health.json"
if python3 -c '' >/dev/null 2>&1; then health_python=python3
elif python -c '' >/dev/null 2>&1; then health_python=python
else fail "cannot validate publication health: Python unavailable"; fi
"$health_python" - "$health_file" "$publish_start" <<'PY' || fail "publication health missing, invalid or older than this invocation"
import json, sys
from datetime import datetime
with open(sys.argv[1], encoding="utf-8") as stream:
    health = json.load(stream)
stamp = datetime.fromisoformat(health["ts"].replace("Z", "+00:00"))
start = datetime.fromisoformat(sys.argv[2].replace("Z", "+00:00"))
if stamp.tzinfo is None or stamp < start:
    raise ValueError("publication health predates this invocation")
if health["phase"] != "publish" or type(health["rc"]) is not int or health["rc"] != 0:
    raise ValueError("publication did not succeed")
PY
bash "$REPO_ROOT/scripts/notify.sh" cron equality-matrix pass "matrix rebuilt + published" || true
echo "equality-matrix-cron OK"
