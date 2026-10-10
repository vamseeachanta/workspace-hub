# PR 4036 Code Review — Fleet Snapshot Daily Writer

Reviewed-At: 2026-10-10
Reviewed-By: Codex
Reviewed-Range: origin/main...HEAD
Verdict: APPROVE

## Scope Reviewed

- Merge resolution for draft PR #4036 after PR #4026 and PR #3969 landed on main.
- Retirement of committed dated fleet snapshot files under `docs/reports/fleet-snapshots/`.
- S01 latest-only assertion in `tests/fleet/test_fleet_snapshot_labels.py`.
- Scheduler mutation digest regeneration after the merge.

## Adversarial Findings

No blocking findings.

The main conflict risk was that the PR could preserve relabelled dated snapshots while main also carried relabel changes. The resolution first restored the snapshot directory from `origin/main`, then applied owner decision E03 by removing every tracked `YYYY-MM-DD.json` snapshot while keeping `latest.json`. The resulting tree has only `docs/reports/fleet-snapshots/latest.json`, and the strict xfail was removed so S01 now asserts the final state directly.

The second risk was stale scheduler governance evidence after the main merge. The cron identity inventory and scheduler mutation HTML were regenerated through the documented sequence, then the four scheduler checks passed.

## Verification

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/fleet -q` -> 80 passed.
- Scheduler guard sequence:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/cron/build-cron-identity-inventory.py --check`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/cron/validate-schedule.py` -> `OK: 71 tasks validated in schedule-tasks.yaml`.
- `UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools uv tool run ruff check tests/fleet/test_fleet_snapshot_daily.py tests/fleet/test_fleet_snapshot_labels.py` -> pass.
- `bash -n scripts/fleet/account-usage-cron.sh scripts/fleet/fleet-snapshot-daily.sh` -> pass.
- `git diff --check` -> pass.
- `/home/vamsee/ws/_codex-jobs/scope-check.sh /home/vamsee/ws/_wt/codex-sr4027 1730cde1c2c748203be2debcab5903c29fc5b130 <dated snapshot removals>` -> `SCOPE-CHECK OK`.
