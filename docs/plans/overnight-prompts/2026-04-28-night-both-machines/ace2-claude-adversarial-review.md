# B3 — ace-linux-2 Claude adversarial review lane

You are running on `ace-linux-2` via a login shell in Claude Code plan/read-only mode. Do not ask the user questions. Do not edit code. Do not commit. Do not mutate GitHub labels/state.

## Mission

Use Claude for long-context adversarial review of the ace-linux-2 implementation lanes and the approved engineering plans. This lane is intentionally read-only so it can run concurrently without git contention.

## Allowed writes

Only write reports under:

`/mnt/local-analysis/ace2-worker-reports/`

Preferred output files:

- `/mnt/local-analysis/ace2-worker-reports/night-20260428-adversarial-review-digitalmodel.md`
- `/mnt/local-analysis/ace2-worker-reports/night-20260428-adversarial-review-knowledge.md`
- `/mnt/local-analysis/ace2-worker-reports/night-20260428-adversarial-review-summary.md`

## Review targets

1. #2515 plan and any B1 implementation evidence/logs.
2. #2458 plan/current state and any B1 evidence/logs.
3. B2 knowledge/doc-intel queue: #2364, #2368, #2369, #2373, #2403, #2227.
4. Remote logs under `/mnt/local-analysis/ace2-worker-logs/*20260428*` and reports under `/mnt/local-analysis/ace2-worker-reports/*20260428*` if present.

## Required verdict format

For each reviewed issue, return one of:

- `APPROVE` — evidence satisfies plan/issue acceptance criteria.
- `MINOR` — safe to proceed but has small cleanup/follow-up.
- `MAJOR` — do not close/merge; specific blocker must be fixed.
- `INSUFFICIENT_EVIDENCE` — implementation may be fine but verification/log/commit evidence is missing.

Each finding must include:

- issue number and URL
- exact evidence inspected
- file/line references when available
- specific fix or verification command
- whether this should block morning closeout

## Special checks

- Confirm B1 did not commit digitalmodel changes from the workspace-hub parent repo.
- Confirm B2 did not overlap with B1 files or broad-commit dirty parent files.
- Check that every claimed implementation has test output or an explicit blocker.
- Check that any `status:needs-data` issue (#2227) did not fabricate missing source data.
