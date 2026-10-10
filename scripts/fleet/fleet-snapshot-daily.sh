#!/usr/bin/env bash
# fleet-snapshot-daily.sh -- repo-owned daily fleet snapshot commit wrapper.
#
# The collector VM scheduler should point at this script. The snapshot producer
# writes JSON to $FLEET_SNAPSHOT_OUT, or an already-created JSON file is supplied
# through $FLEET_SNAPSHOT_SOURCE. This wrapper owns the public commit path:
# label first, replace docs/reports/fleet-snapshots/latest.json only, then stage.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="${FLEET_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
SNAPSHOT_REL="docs/reports/fleet-snapshots/latest.json"
SNAPSHOT="${HUB}/${SNAPSHOT_REL}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

usage() {
    cat <<'EOF'
Usage:
  FLEET_SNAPSHOT_COLLECT_CMD='<collector command>' bash scripts/fleet/fleet-snapshot-daily.sh
  FLEET_SNAPSHOT_SOURCE=/path/to/snapshot.json bash scripts/fleet/fleet-snapshot-daily.sh
  bash scripts/fleet/fleet-snapshot-daily.sh --print-scheduler-entry

The collector command receives FLEET_SNAPSHOT_OUT as the path it must write.
The script never writes dated snapshot files; it overwrites latest.json only.
EOF
}

print_scheduler_entry() {
    cat <<'EOF'
# Owner step: point the collector VM scheduler at the repo-owned wrapper.
# Fill in the existing collector command; it must write JSON to FLEET_SNAPSHOT_OUT.
FLEET_HUB=$WORKSPACE_HUB FLEET_SNAPSHOT_COLLECT_CMD='<existing collector command>' \
  bash scripts/fleet/fleet-snapshot-daily.sh >> logs/fleet/fleet-snapshot-daily.log 2>&1
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi
if [[ "${1:-}" == "--print-scheduler-entry" ]]; then
    print_scheduler_entry
    exit 0
fi
if [[ $# -gt 0 ]]; then
    usage >&2
    exit 2
fi

cd "${HUB}"
echo "== fleet-snapshot-daily ${STAMP} (${HUB}) =="

if [[ -n "${FLEET_SNAPSHOT_SOURCE:-}" && -n "${FLEET_SNAPSHOT_COLLECT_CMD:-}" ]]; then
    echo "snapshot: set either FLEET_SNAPSHOT_SOURCE or FLEET_SNAPSHOT_COLLECT_CMD, not both" >&2
    exit 2
fi
if [[ -z "${FLEET_SNAPSHOT_SOURCE:-}" && -z "${FLEET_SNAPSHOT_COLLECT_CMD:-}" ]]; then
    echo "snapshot: missing source; run --print-scheduler-entry for the owner step" >&2
    exit 2
fi

mkdir -p "$(dirname "${SNAPSHOT}")"
if ! git diff --quiet -- "${SNAPSHOT_REL}" || ! git diff --cached --quiet -- "${SNAPSHOT_REL}"; then
    echo "snapshot: ${SNAPSHOT_REL} has local changes; refusing to overwrite" >&2
    exit 2
fi
if git remote get-url origin >/dev/null 2>&1; then
    git pull --ff-only --quiet origin main || {
        echo "pull: not fast-forwardable; nothing published" >&2
        exit 1
    }
fi

TMP_SNAPSHOT="$(mktemp "${TMPDIR:-/tmp}/fleet-snapshot.XXXXXX.json")"
cleanup() {
    rm -f "${TMP_SNAPSHOT}"
}
trap cleanup EXIT

if [[ -n "${FLEET_SNAPSHOT_SOURCE:-}" ]]; then
    cp -- "${FLEET_SNAPSHOT_SOURCE}" "${TMP_SNAPSHOT}"
else
    FLEET_SNAPSHOT_OUT="${TMP_SNAPSHOT}" bash -euo pipefail -c "${FLEET_SNAPSHOT_COLLECT_CMD}"
fi
python3 -m json.tool "${TMP_SNAPSHOT}" >/dev/null
if ! python3 scripts/fleet/fleet_snapshot_labels.py "${TMP_SNAPSHOT}"; then
    echo "labels: refused latest.json; no commit made" >&2
    exit 2
fi

install -m 0644 "${TMP_SNAPSHOT}" "${SNAPSHOT}"
git add -- "${SNAPSHOT_REL}"
if git diff --cached --quiet -- "${SNAPSHOT_REL}"; then
    echo "commit: no change"
    exit 0
fi
git commit --quiet -m "chore(reports): fleet snapshot latest [skip ci]" -- "${SNAPSHOT_REL}"
echo "commit: $(git rev-parse --short HEAD)"

if [[ "${FLEET_NO_PUSH:-0}" == "1" ]]; then
    echo "push: skipped (FLEET_NO_PUSH)"
    exit 0
fi
git push --quiet origin HEAD:main
echo "push: ok"
