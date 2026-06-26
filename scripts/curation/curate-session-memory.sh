#!/usr/bin/env bash
# curate-session-memory.sh — fail-loud cron wrapper for the session-analysis + memory-curation
# line item of the machine-equality matrix. Cross-platform (Linux/macOS/Windows-Git-Bash).
#
# Flow: curate (analyze provider logs + memory delta, publish fingerprint to the
# session-curation-state ref) -> refresh THIS box's equality column (collect + matrix build),
# so a healthy box always shows the cell green and an up-to-date render every 6h.
# On ANY hard failure emits a JSONL notification (scripts/notify.sh) and exits non-zero.
set -uo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo "/mnt/local-analysis/workspace-hub")"
cd "$REPO_ROOT" || { echo "curate-session-memory: cannot cd to repo root" >&2; exit 1; }

fail() {
  bash "$REPO_ROOT/scripts/notify.sh" cron session-curation fail "$1" || true
  echo "curate-session-memory FAIL: $1" >&2
  exit 1
}

# Pick a python that resolves pyyaml: prefer the PEP-723 uv path, fall back to python3.
ENGINE="$REPO_ROOT/scripts/curation/curate_session_memory.py"
if command -v uv >/dev/null 2>&1; then
  uv run --no-project --with pyyaml python "$ENGINE" || fail "curation engine failed (uv)"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$ENGINE" || fail "curation engine failed (python3)"
else
  fail "no python runtime (uv/python3) available"
fi

# Audit cross-provider skill currency (#3249) — writes skill-currency-<machine>.json for the
# skill_currency matrix cell. Best-effort: a failed audit must not block the curation run.
SKILL_AUDIT="$REPO_ROOT/scripts/curation/audit_skill_currency.py"
if command -v uv >/dev/null 2>&1; then
  uv run --no-project --with pyyaml python "$SKILL_AUDIT" || echo "skill-currency audit failed (soft)" >&2
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SKILL_AUDIT" || echo "skill-currency audit failed (soft)" >&2
fi

# Refresh this box's equality column so the freshness cell + render are current. The matrix
# build is NOT optional — skipping it would freeze the rendered cell (weakening the dead-man's
# switch) while still reporting pass. So fail loudly if no python can build it.
bash "$REPO_ROOT/scripts/readiness/collect-equality.sh" || fail "collect-equality.sh failed"
MATRIX="$REPO_ROOT/scripts/readiness/build-equality-matrix.py"
if command -v uv >/dev/null 2>&1; then
  uv run --no-project --with pyyaml python "$MATRIX" || fail "build-equality-matrix.py failed (uv)"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$MATRIX" || fail "build-equality-matrix.py failed (python3 — pyyaml installed?)"
else
  fail "no python runtime to rebuild the equality matrix"
fi

bash "$REPO_ROOT/scripts/notify.sh" cron session-curation pass "curated + matrix refreshed" || true
echo "curate-session-memory OK"
