#!/usr/bin/env bash
# sync-cadence-helper.sh — Verify the cadence-common.sh helper is byte-identical
# between workspace-hub and the worldenergydata vendored copy.
#
# Issue: worldenergydata#309 + workspace-hub#2316/2317/etc (shared cadence design)
# Design: docs/plans/2026-04-17-cadence-cron-infrastructure.md §cross-repo
#
# Exits 0 when the two copies agree, exits 1 on sha256 drift. Wired into
# pre-push by scripts/enforcement/install-hooks.sh so any push that modifies
# one copy without the other is blocked.
#
# Usage:
#   bash scripts/sync/sync-cadence-helper.sh           # strict check (exit 1 on drift)
#   bash scripts/sync/sync-cadence-helper.sh --fix     # copy workspace-hub → wed
#
# Env overrides (testing):
#   CADENCE_CANONICAL   — path to the source of truth (default scripts/cron/lib/...)
#   CADENCE_VENDORED    — path to the vendored copy (default worldenergydata/scripts/...)
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CANONICAL="${CADENCE_CANONICAL:-${REPO_ROOT}/scripts/cron/lib/cadence-common.sh}"
VENDORED="${CADENCE_VENDORED:-${REPO_ROOT}/worldenergydata/scripts/cron/lib/cadence-common.sh}"

FIX=0
for arg in "$@"; do
    case "$arg" in
        --fix) FIX=1 ;;
        --help)
            sed -n '1,20p' "$0"
            exit 0
            ;;
    esac
done

# Canonical must always exist.
if [[ ! -f "$CANONICAL" ]]; then
    echo "[sync-cadence-helper] ERROR: canonical helper missing at ${CANONICAL}" >&2
    exit 1
fi

# Vendored copy may be absent when worldenergydata isn't cloned. That's OK —
# pre-push in workspace-hub only cares when both are present.
if [[ ! -f "$VENDORED" ]]; then
    echo "[sync-cadence-helper] OK: vendored copy not present (worldenergydata absent)"
    exit 0
fi

sum_canonical="$(sha256sum "$CANONICAL" | awk '{print $1}')"
sum_vendored="$(sha256sum "$VENDORED" | awk '{print $1}')"

if [[ "$sum_canonical" == "$sum_vendored" ]]; then
    echo "[sync-cadence-helper] OK: both copies sha256=${sum_canonical:0:12}…"
    exit 0
fi

echo "[sync-cadence-helper] DRIFT:" >&2
echo "  canonical: ${sum_canonical:0:12}… (${CANONICAL#$REPO_ROOT/})" >&2
echo "  vendored:  ${sum_vendored:0:12}… (${VENDORED#$REPO_ROOT/})" >&2

if (( FIX == 1 )); then
    cp "$CANONICAL" "$VENDORED"
    echo "[sync-cadence-helper] FIX: copied canonical → vendored" >&2
    exit 0
fi

echo "[sync-cadence-helper] FAIL: cadence-common.sh copies drifted." >&2
echo "  Fix with: bash scripts/sync/sync-cadence-helper.sh --fix" >&2
echo "  Or edit both files identically and re-run this check." >&2
exit 1
