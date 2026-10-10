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
LOCK_PATH="${FLEET_PUBLISH_LOCK:-${HUB}/.git/fleet-publish.lock}"
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
    printf '%s\n' '# Owner step: point the collector VM scheduler at the repo-owned wrapper.'
    printf '%s\n' '# Fill in the existing collector command; it must write JSON to FLEET_SNAPSHOT_OUT.'
    printf 'cd %q && FLEET_HUB=%q FLEET_SNAPSHOT_COLLECT_CMD='\''<existing collector command>'\'' bash %q >> %q 2>&1\n' \
        "${HUB}" "${HUB}" "${HUB}/scripts/fleet/fleet-snapshot-daily.sh" \
        "${HUB}/logs/fleet/fleet-snapshot-daily.log"
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

branch="$(git symbolic-ref --quiet --short HEAD || true)"
if [[ "${branch}" != "main" ]]; then
    echo "snapshot: must run on main; current branch is ${branch:-detached}" >&2
    exit 2
fi

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
    git fetch --quiet origin main
    if [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]]; then
        echo "snapshot: main is not at origin/main; nothing published" >&2
        exit 1
    fi
fi

mkdir -p "$(dirname "${LOCK_PATH}")"
exec 9>"${LOCK_PATH}"
flock 9

TMP_SNAPSHOT="$(mktemp "$(dirname "${SNAPSHOT}")/.latest.XXXXXX.json")"
COLLECT_LOG="$(mktemp "${TMPDIR:-/tmp}/fleet-snapshot-collector.XXXXXX.log")"
installed=0
committed=0
cleanup() {
    rc=$?
    if (( rc != 0 && installed == 1 && committed == 0 )); then
        git reset -q HEAD -- "${SNAPSHOT_REL}" 2>/dev/null || true
        git checkout -- "${SNAPSHOT_REL}" 2>/dev/null || true
    fi
    rm -f "${TMP_SNAPSHOT}"
    if (( rc == 0 )); then
        rm -f "${COLLECT_LOG}"
    fi
}
trap cleanup EXIT

if [[ -n "${FLEET_SNAPSHOT_SOURCE:-}" ]]; then
    cp -- "${FLEET_SNAPSHOT_SOURCE}" "${TMP_SNAPSHOT}"
else
    rc=0
    FLEET_SNAPSHOT_OUT="${TMP_SNAPSHOT}" bash -euo pipefail -c "${FLEET_SNAPSHOT_COLLECT_CMD}" >"${COLLECT_LOG}" 2>&1 || rc=$?
    if (( rc != 0 )); then
        echo "collect: failed (exit ${rc}); raw collector log kept outside the repo at ${COLLECT_LOG}" >&2
        exit "${rc}"
    fi
fi
python3 -m json.tool "${TMP_SNAPSHOT}" >/dev/null
if ! python3 scripts/fleet/fleet_snapshot_labels.py "${TMP_SNAPSHOT}"; then
    echo "labels: refused latest.json; no commit made" >&2
    exit 2
fi

mv -- "${TMP_SNAPSHOT}" "${SNAPSHOT}"
chmod 0644 "${SNAPSHOT}"
installed=1
git add -- "${SNAPSHOT_REL}"
mapfile -t staged_paths < <(git diff --cached --name-only)
if (( ${#staged_paths[@]} > 0 )) \
    && { (( ${#staged_paths[@]} != 1 )) || [[ "${staged_paths[0]}" != "${SNAPSHOT_REL}" ]]; }; then
    echo "commit: refusing staged paths outside ${SNAPSHOT_REL}" >&2
    exit 2
fi
if git diff --cached --quiet -- "${SNAPSHOT_REL}"; then
    echo "commit: no change"
    exit 0
fi
git commit --quiet -m "chore(reports): fleet snapshot latest [skip ci]" -- "${SNAPSHOT_REL}"
committed=1
echo "commit: $(git rev-parse --short HEAD)"

if [[ "${FLEET_NO_PUSH:-0}" == "1" ]]; then
    echo "push: skipped (FLEET_NO_PUSH)"
    exit 0
fi
if git push --quiet origin HEAD:main; then
    echo "push: ok"
elif git fetch --quiet origin main && git merge-base --is-ancestor origin/main HEAD \
    && git push --quiet origin HEAD:main; then
    echo "push: ok after retry"
else
    echo "push: FAILED (left committed locally; next run requires operator recovery)" >&2
    exit 1
fi
