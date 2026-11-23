# /goal Swarm 5 — Learning transfer, skills, and durable process correction audit

Audit the workspace-hub ecosystem for reusable learnings, missing skill updates, and process-correction opportunities from recent work, then produce a learning-transfer report.

You are operating in:

`/mnt/local-analysis/workspace-hub`

Do not ask the user questions.

Hard constraints:
- This is audit/report-only.
- Do not create, edit, or delete skills.
- Do not edit memory.
- Do not implement code.
- Do not change GitHub labels.
- Do not close issues.
- Produce recommendations only.

Allowed write path:
- `docs/plans/agent-swarm-audits/2026-05-10/swarm-5-learning-transfer.md`

Forbidden write paths:
- `.claude/skills/`
- Any source code
- Any tests
- Any `.planning/` approval marker
- Any files owned by the other swarms:
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-1-live-state-gate-audit.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-2-capability-gap-map.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-3-plan-review-drift.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-4-execution-readiness-partition.md`

Required work:
1. Inspect recent handoffs, docs/plans, docs/session-handoffs, issue closeout evidence, and relevant skills.
2. Identify repeated failure modes or workflow lessons involving branch/worktree cleanup, transactional issue closeout, stale plan-review artifacts, approval drift, multi-agent contention, nested repo limitations, verification gaps, and docs/report/skill-transfer changes needing adversarial review.
3. For each learning candidate, classify: already captured in an existing skill, should patch an existing class-level skill, should become a new skill, should remain as local session artifact only, or not durable / no action.
4. Recommend exact skill names or existing skill files to patch, but do not patch them.
5. Identify any memories that would be inappropriate because they are stale/task-specific.
6. Produce a “Nothing to save” section only if truly no durable signal exists.

Required artifact sections:
- Executive summary
- Recent signal sources inspected
- Durable learnings found
- Existing skills that may need patches
- Candidate new skills
- Non-durable items intentionally not saved
- Recommended next operator actions

Verification:
- Every proposed skill update must cite the source artifact and the existing skill that should absorb it.
- Do not create low-value “completed task” memories.

Final output:
Return only:
1. Artifact path written
2. Number of durable learning candidates
3. Existing skills recommended for patch
4. New skills recommended
5. Items intentionally not saved
