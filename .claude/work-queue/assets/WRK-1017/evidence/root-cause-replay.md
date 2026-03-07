# Root Cause Replay — WRK-1017

Goal: confirm how Stage 5 was skipped in the observed `WRK-1015` path.

Evidence inspected:
- `.claude/work-queue/assets/WRK-1015/evidence/stage-evidence.yaml`
- `.claude/work-queue/assets/WRK-1015/evidence/` directory contents
- `.claude/work-queue/archive/2026-03/WRK-1015.md`

Findings:
1. `WRK-1015` stage evidence marks Stage 5 `done` with evidence `.claude/work-queue/assets/WRK-1015/evidence/user-review-browser-open.yaml` and note `user approved in session 2026-03-05`.
2. The `WRK-1015` evidence directory does not contain `user-review-plan-draft.yaml`.
3. `WRK-1015` frontmatter still ended at `plan_approved: true` and `plan_reviewed: true`, so later stages progressed without the structured Stage 5 decision artifact that `WRK-1017` is introducing.

Conclusion:
- The confirmed bypass mode is insufficient Stage 5 evidence progression: browser-open evidence plus free-text/session notes were enough to advance the lifecycle.
- This proves the fix must enforce a canonical machine-checkable Stage 5 evidence predicate at the entrypoint/checker layer.
- Artifact replay alone does not prove whether the stage advancement was triggered by an official entrypoint or by direct manual mutation, but it does prove the workflow advanced without the required structured decision artifact.
