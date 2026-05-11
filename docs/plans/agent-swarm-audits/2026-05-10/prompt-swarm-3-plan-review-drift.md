# /goal Swarm 3 — Plan-review queue + approval-drift reconciliation

Audit the current plan-review and plan-approved queues for approval drift, stale plans, and unsafe execution candidates.

You are operating in:

`/mnt/local-analysis/workspace-hub`

Do not ask the user questions.

Hard constraints:
- This is governance/audit-only.
- Do not implement code.
- Do not modify issue labels.
- Do not close issues.
- Do not approve plans.
- Do not create `.planning/` approval markers.
- The user must explicitly approve plans before implementation.

Allowed write path:
- `docs/plans/agent-swarm-audits/2026-05-10/swarm-3-plan-review-drift.md`

Forbidden write paths:
- Any source code
- Any tests
- Any `.planning/` approval marker
- Any files owned by the other swarms:
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-1-live-state-gate-audit.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-2-capability-gap-map.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-4-execution-readiness-partition.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-5-learning-transfer.md`

Required work:
1. Inspect GitHub issues in this repo where possible, especially labels: `status:plan-review`, `status:plan-approved`, `status:blocked`, `status:in-progress`.
2. Inspect local plan files under `docs/plans/`.
3. Identify issues labeled plan-review but lacking a plan artifact; issues labeled plan-approved but lacking durable approval evidence; plan files with stale or missing adversarial review evidence; plans whose issue body/comments no longer match the local artifact; plans overtaken by later commits or handoffs; closed issues with unresolved cleanup/worktree/state concerns.
4. For each suspect issue, classify: SAFE TO KEEP IN PLAN-REVIEW, NEEDS REREVIEW, NEEDS USER APPROVAL SYNC, NEEDS BLOCKER COMMENT, POSSIBLE VERIFY/CLOSE CANDIDATE, or UNSAFE TO EXECUTE.
5. Produce an operator-ready reconciliation report with exact commands/comments the operator could run later, but do not run them.

Required output structure in the artifact:
- Executive summary
- Queue inventory
- Approval-drift findings
- Unsafe execution candidates
- Suggested label/comment command pack, clearly marked “DRAFT — DO NOT RUN AUTOMATICALLY”
- Recommended next actions

Verification:
- Ground every finding in issue URL, label state, local file path, or git evidence.
- Do not rely on stale prompt packs as authority.

Final output:
Return only:
1. Artifact path written
2. Count of plan-review issues inspected
3. Count of plan-approved issues inspected
4. Issues unsafe to execute
5. Draft operator actions generated
