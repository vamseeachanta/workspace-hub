# Wave 2 / Wave 3 Plan Review Status — 2026-04-27

Recovery note: the post-reboot manual fanout stalled/restarted across provider CLIs. To avoid duplicate spend, stale fanout processes were stopped; non-empty artifacts are retained, empty attempted artifacts were converted to explicit `UNAVAILABLE` stubs, and unattempted plans remain `PENDING` for the next scheduled review pass.

| Wave | Issue | Plan | Claude | Codex | Gemini | Next action |
|---|---:|---|---|---|---|---|
| wave 2 | #2509 | `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 2 | #2378 | `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 2 | #2375 | `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 2 | #2301 | `docs/plans/2026-04-26-issue-2301-hermes-codex-transport-classify.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 2 | #2291 | `docs/plans/2026-04-26-issue-2291-cron-health-failure-detection.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 3 | #2507 | `docs/plans/2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Review signals captured only if provider verdict is non-UNAVAILABLE; otherwise retry after fanout hardening. |
| wave 3 | #2374 | `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` | PENDING | PENDING | PENDING | Scheduled for future bounded retry; do not auto-approve. |
| wave 3 | #2372 | `docs/plans/2026-04-27-issue-2372-wiki-source-title-aliasing.md` | PENDING | PENDING | PENDING | Scheduled for future bounded retry; do not auto-approve. |
| wave 3 | #2506 | `docs/plans/2026-04-27-issue-2506-lane-e-handoff-readiness-validator.md` | PENDING | PENDING | PENDING | Scheduled for future bounded retry; do not auto-approve. |
| wave 3 | #2500 | `docs/plans/2026-04-27-issue-2500-2476-non-standard-approval-pattern.md` | PENDING | PENDING | PENDING | Scheduled for future bounded retry; do not auto-approve. |

## Observed provider/fanout failures

- Gemini CLI returned rc=55: workspace trust not configured; future runs should set `GEMINI_CLI_TRUST_WORKSPACE=true` or use `--skip-trust` from a trusted cwd.
- Codex CLI emitted session output to `.err` while canonical `.md` stayed empty/UNAVAILABLE for interrupted runs; future wrapper should capture/normalize both stdout and stderr.
- Claude/fanout processes were terminated during reboot recovery after long stalls; no approval labels were changed.
| wave 3 | #2507 | `docs/plans/2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md` | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | — |
