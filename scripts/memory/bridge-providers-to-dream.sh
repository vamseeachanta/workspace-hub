#!/usr/bin/env bash
# bridge-providers-to-dream.sh — Feed Codex/Gemini/Hermes sessions into the Claude dream.
#
# WHY: Claude Code's dreaming only ingests its own auto-memory + its own session
#   transcripts. This wrapper runs the cross-provider distiller so the dream
#   becomes THE cross-provider consolidator (per the user's decision; see
#   reference_claude_dreaming_managed_agents.md). The distiller reads other-
#   provider sessions, distills durable learnings via Claude (headless `claude -p`), and
#   writes provenance-tagged memory files the dream then consolidates/prunes.
#
# USAGE:
#   bash bridge-providers-to-dream.sh                 # incremental (since watermark)
#   bash bridge-providers-to-dream.sh --backfill      # all history (token-heavy)
#   bash bridge-providers-to-dream.sh --dry-run --limit 3   # prove pipeline, write nothing
#   (extra args are passed straight through to the Python distiller)
#
# SCHEDULING: cron 04:00 daily (mirrors bridge-hermes-claude.sh). Install with
#   scripts/memory/install-provider-bridge-cron.sh (separate, needs user auth).
#
# LOGGING: appends to logs/orchestrator/memory-bridge/<date>.log under the repo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "/mnt/local-analysis/workspace-hub")"
DISTILLER="${SCRIPT_DIR}/distill-provider-sessions.py"

LOG_DIR="${REPO_ROOT}/logs/orchestrator/memory-bridge"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/$(date +%Y-%m-%d).log"

# Prefer uv (Linux Python rule) but the distiller is stdlib-only, so plain
# python3 is a fine fallback (and the only option on Windows / no-uv hosts).
if command -v uv >/dev/null 2>&1 && uv run --no-project python -c "print(1)" >/dev/null 2>&1; then
  PY=(uv run --no-project python)
else
  PY=(python3)
fi

echo "[bridge-to-dream] $(date -u +%Y-%m-%dT%H:%M:%SZ) starting (args: $*)" | tee -a "$LOG_FILE"

# The distiller logs+continues on a single provider's transient failure, but it
# exits non-zero when sessions were DEAD-LETTERED (rc=3, #2845) or on a hard
# error. We capture its rc and surface a WARN so cron mail/log review catches it
# instead of a green "done" masking lost learnings.
set +e
"${PY[@]}" "$DISTILLER" "$@" 2>&1 | tee -a "$LOG_FILE"
rc=${PIPESTATUS[0]}
set -e

if [ "$rc" -eq 3 ]; then
  echo "[bridge-to-dream] WARN $(date -u +%Y-%m-%dT%H:%M:%SZ) distiller DEAD-LETTERED session(s) — " \
       "inspect ~/.claude/projects/*/memory/.provider-bridge-deadletter.jsonl (#2845)" | tee -a "$LOG_FILE"
elif [ "$rc" -ne 0 ]; then
  echo "[bridge-to-dream] WARN $(date -u +%Y-%m-%dT%H:%M:%SZ) distiller exited rc=$rc (hard failure)" | tee -a "$LOG_FILE"
fi

echo "[bridge-to-dream] $(date -u +%Y-%m-%dT%H:%M:%SZ) done (rc=$rc)" | tee -a "$LOG_FILE"
exit "$rc"
