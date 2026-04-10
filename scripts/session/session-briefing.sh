#!/usr/bin/env bash
# session-briefing.sh — Consolidated session-start briefing output.
# Wraps snapshot-age.sh + quota-status.sh + legacy whats-next.sh compatibility wrapper (--all).
# Non-blocking by design: each section runs independently; always exits 0.
# Usage: session-briefing.sh [--category <name>]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
CATEGORY_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --category) CATEGORY_FLAG="--category $2"; shift 2 ;;
    *) shift ;;
  esac
done

# --- Section: Snapshot ---
echo "## Snapshot"
snapshot_out=$(bash "${SCRIPT_DIR}/snapshot-age.sh" 2>/dev/null) || snapshot_out="(unavailable)"
echo "  ${snapshot_out}"

# --- Section: Quota ---
echo ""
echo "## Quota"
quota_out=$(bash "${SCRIPT_DIR}/quota-status.sh" 2>/dev/null) || quota_out=""
if [[ -n "$quota_out" ]]; then
  echo "$quota_out" | sed 's/^/  /'
else
  echo "  (all providers within limits)"
fi

# --- Section: Data Intelligence ---
echo ""
DATA_INTEL="${SCRIPT_DIR}/data-intelligence-context.sh"
if [[ -f "$DATA_INTEL" ]]; then
  # shellcheck disable=SC2086
  intel_out=$(bash "$DATA_INTEL" $CATEGORY_FLAG 2>/dev/null) || intel_out=""
  if [[ -n "$intel_out" ]]; then
    echo "$intel_out"
  fi
fi

# --- Section: Top Unblocked ---
echo ""
echo "## Top Unblocked"
WHATS_NEXT="${REPO_ROOT}/scripts/work-queue/whats-next.sh"
if [[ -f "$WHATS_NEXT" ]]; then
  # shellcheck disable=SC2086
  whats_out=$(bash "$WHATS_NEXT" --all $CATEGORY_FLAG 2>/dev/null) || whats_out="(unavailable)"
  echo "$whats_out" | head -40
else
  echo "  (whats-next.sh not found)"
fi

exit 0
