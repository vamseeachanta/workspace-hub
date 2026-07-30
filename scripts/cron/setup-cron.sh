#!/usr/bin/env bash
# setup-cron.sh — compatibility entrypoint for transactional cron reconciliation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
CRON_RENDER="${WORKSPACE_HUB}/scripts/cron/cron_render.py"
CRON_APPLY="${WORKSPACE_HUB}/scripts/cron/cron_apply.py"
export UV_CACHE_DIR="${UV_CACHE_DIR:-${WORKSPACE_HUB}/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"

DRY_RUN=false
REPLACE=false
ALLOW_LIVE_RELOAD=false
TARGET_MACHINE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --replace) REPLACE=true; shift ;;
    --allow-live-reload) ALLOW_LIVE_RELOAD=true; shift ;;
    --machine)
      [[ $# -ge 2 ]] || { echo "ERROR: --machine requires a value" >&2; exit 2; }
      TARGET_MACHINE="$2"
      shift 2
      ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ "$REPLACE" == true ]]; then
  echo "ERROR: 'setup-cron.sh --replace' is disabled (#2969)" >&2
  echo "Use transactional preview/apply through setup-cron.sh instead." >&2
  exit 2
fi

if [[ -z "$TARGET_MACHINE" ]]; then
  TARGET_MACHINE="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"
fi
PHYSICAL_HOST="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"

CANONICAL_MACHINE="$(uv run --no-project python "$CRON_RENDER" \
  --machine "$TARGET_MACHINE" --field machine_id)"
PHYSICAL_MACHINE="$(uv run --no-project python "$CRON_RENDER" \
  --machine "$PHYSICAL_HOST" --field machine_id)"
SCHEDULE_VARIANT="$(uv run --no-project python "$CRON_RENDER" \
  --machine "$TARGET_MACHINE" --field schedule_variant)"

echo "Host: ${TARGET_MACHINE} → machine: ${CANONICAL_MACHINE} → cron_variant: ${SCHEDULE_VARIANT}"
# #3507: key the Task-Scheduler skip on the registry os field, NOT the schedule
# variant — gpu-claw is a linux contribute-minimal box and must get real crons.
MACHINE_OS="$(uv run --no-project python "$CRON_RENDER" \
  --machine "$TARGET_MACHINE" --field os)"
if [[ "$MACHINE_OS" == "windows" ]]; then
  echo "This machine uses Windows Task Scheduler; Linux cron reconciliation is skipped."
  exit 0
fi
if [[ "$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE" ]]; then
  echo "ERROR: refusing to reconcile local crontab for remote machine ${CANONICAL_MACHINE}" >&2
  echo "Run setup-cron.sh on that machine instead." >&2
  exit 2
fi

APPLY_ARGS=(--machine "$CANONICAL_MACHINE")
if [[ "$DRY_RUN" == false ]]; then
  APPLY_ARGS+=(--apply)
else
  APPLY_ARGS+=(--json)
fi
if [[ "$ALLOW_LIVE_RELOAD" == true ]]; then
  APPLY_ARGS+=(--allow-live-reload)
fi

exec uv run --script "$CRON_APPLY" "${APPLY_ARGS[@]}"
