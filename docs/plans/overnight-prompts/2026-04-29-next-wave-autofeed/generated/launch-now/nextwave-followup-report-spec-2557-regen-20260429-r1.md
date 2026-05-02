Workspace: /mnt/local-analysis/workspace-hub.
Run kind: bounded follow-up planning/review/synthesis only.
Hard guardrails: do not run gh issue edit/comment/close; do not apply status:plan-review or status:plan-approved; do not write .planning/plan-approved markers; do not send outreach; do not commit or push; do not run production implementation; do not overwrite an existing result path. If your result path already exists, stop and write BLOCKED only to the log.
Before editing, re-read current files and live context. Keep changes scoped to the named issue/files. Write the primary result artifact exactly at the requested path with: summary, files inspected, files changed if any, remaining blockers, and next safe action.

Issue: #2557 weekly productivity-flow review and hacks.
Task: write a regeneration/spec packet only: identify exact source files, live data headers, stale-stat corrections, canonical root, and BL-1..BL-7 ownership needed before safely regenerating the productivity-flow report. Do not regenerate the report unless all inputs are verified and remain planning/report-only; default to spec-only.
Inputs: docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md; docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-blocker-packet-2557-20260429-1559.md; provider report files only for read-only verification.
Result path: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-report-spec-2557-regen-20260429-r1.md
