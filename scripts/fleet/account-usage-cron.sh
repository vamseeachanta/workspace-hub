#!/usr/bin/env bash
# account-usage-cron.sh — hourly on the fleet collector VM: probe every fleet
# host's Claude/Codex account usage, publish the per-account aggregate, push.
#
# Installed by scripts/fleet/install-fleet-collector-cron.sh. Safe to run by
# hand. Never discards local work: pull is ff-only and a diverged checkout is
# reported, not reset. Commits only the two generated files and only when
# they changed; the commit carries [skip ci] so hourly refreshes do not burn
# Actions minutes.
#
# Env: FLEET_HUB (repo root; default = this script's repo), FLEET_NO_PUSH=1
#      (write + commit, no push), FLEET_HOSTS=a,b (subset).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="${FLEET_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
OUT="config/ai-tools/account-usage-latest.json"
MD="docs/reports/ai-account-usage.md"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cd "${HUB}"
echo "== account-usage-cron ${STAMP} (${HUB}) =="

# 1. Freshen main without touching local edits. A diverged main is a human's
#    problem; we still publish from what we have.
if git pull --ff-only --quiet origin main 2>/dev/null; then
    echo "pull: ff to $(git rev-parse --short HEAD)"
else
    echo "pull: not fast-forwardable (dirty or diverged); publishing from $(git rev-parse --short HEAD)"
fi

# 2. Collect + aggregate. Exit 1 = no host answered; keep the previous files.
hosts_arg=()
[[ -n "${FLEET_HOSTS:-}" ]] && hosts_arg=(--hosts "${FLEET_HOSTS}")
if ! python3 scripts/fleet/collect_account_usage_fleet.py --out "${OUT}" --md "${MD}" "${hosts_arg[@]}"; then
    echo "collect: no host answered; nothing published"
    exit 1
fi

# 3. Commit only the generated files, only if they changed.
git add -- "${OUT}" "${MD}"
if git diff --cached --quiet -- "${OUT}" "${MD}"; then
    echo "commit: no change"
    exit 0
fi
# Author = the VM's own git identity (the one the daily fleet snapshot uses).
git commit --quiet -m "chore(fleet): AI account usage ${STAMP} [skip ci]" -- "${OUT}" "${MD}"
echo "commit: $(git rev-parse --short HEAD)"

[[ "${FLEET_NO_PUSH:-0}" == "1" ]] && { echo "push: skipped (FLEET_NO_PUSH)"; exit 0; }

# 4. Push; on a race, rebase our single commit once and retry.
if git push --quiet origin HEAD:main; then
    echo "push: ok"
elif git pull --rebase --quiet origin main && git push --quiet origin HEAD:main; then
    echo "push: ok after rebase"
else
    echo "push: FAILED (left committed locally; next run retries)" >&2
    exit 1
fi
