#!/usr/bin/env bash
#
# kanban-autoload.sh — replay the git-tracked kanban YAML source-of-truth
# (.claude/memory/kanban/boards/*.yaml) into THIS machine's local Hermes
# (~/.hermes/kanban.db) via the loader, so board data populates without a
# manual step. Installed as a post-merge hook by bootstrap-machine.sh, and
# also run once at the end of bootstrap.
#
# OPT-IN and gated — safe by default:
#   * Runs ONLY if the opt-in marker exists:  $HERMES_HOME/kanban-autoload.enabled
#     (create with: touch ~/.hermes/kanban-autoload.enabled)
#   * In --from-hook mode, runs only when the pull actually changed board YAML.
#   * Skips silently if the hermes CLI or the loader isn't present.
#
# SAFETY: the loader creates cards with their real status (ready/blocked), not
# forced triage. Enable this ONLY on machines whose Hermes orchestration is
# Manual — on an auto-dispatch machine, loaded `ready` cards (or
# blocked-without-reason, which the gateway auto-unblocks) could be claimed and
# spawn workers. See .claude/memory/kanban/README.md.
#
set -uo pipefail

from_hook=false
[ "${1:-}" = "--from-hook" ] && from_hook=true

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
MARKER="${HERMES_HOME}/kanban-autoload.enabled"
LOADER="${REPO_ROOT}/.claude/memory/kanban/scripts/load.py"

# Gate 1: opt-in marker. Absent => no-op (silent from a hook).
if [ ! -f "${MARKER}" ]; then
  $from_hook || echo "[kanban-autoload] not enabled — create ${MARKER} to opt in (Manual-orchestration machines only)."
  exit 0
fi

# Gate 2: prerequisites present.
command -v hermes >/dev/null 2>&1 || { echo "[kanban-autoload] hermes CLI not found — skipping."; exit 0; }
[ -f "${LOADER}" ] || { echo "[kanban-autoload] loader not found at ${LOADER} — skipping."; exit 0; }

# Gate 3 (hook mode only): skip unless this pull actually changed board YAML.
if $from_hook; then
  if git -C "${REPO_ROOT}" rev-parse ORIG_HEAD >/dev/null 2>&1; then
    if git -C "${REPO_ROOT}" diff --quiet ORIG_HEAD HEAD -- .claude/memory/kanban/boards/ 2>/dev/null; then
      exit 0   # no board changes in this merge
    fi
  fi
fi

echo "[kanban-autoload] replaying kanban YAML -> local Hermes (idempotent)..."
if command -v uv >/dev/null 2>&1; then
  uv run python "${LOADER}" || python3 "${LOADER}" || true
else
  python3 "${LOADER}" || true
fi
echo "[kanban-autoload] done."
