# /goal Swarm 1 — Ecosystem live-state + workflow gate audit

Run a read-only live-state audit of the workspace-hub tier-1 repo ecosystem and produce an operator-ready report.

You are operating in:

`/mnt/local-analysis/workspace-hub`

Tier-1 ecosystem scope:
- workspace-hub
- digitalmodel
- assetutilities
- worldenergydata
- llm-wiki
- assethold
- aceengineer-website
- aceengineer-strategy

Do not ask the user questions.

Hard constraints:
- This is audit/planning-only.
- Do not implement code changes.
- Do not close issues.
- Do not change GitHub labels.
- Do not modify files outside the allowed write path.
- Respect workspace-hub hard gates: Issue → Resource Intel → Plan → Adversarial Review → status:plan-review → USER APPROVES → status:plan-approved → Implement → Cross-review → Close.
- TDD is mandatory for future implementation, but this run must not implement.

Allowed write path:
- `docs/plans/agent-swarm-audits/2026-05-10/swarm-1-live-state-gate-audit.md`

Forbidden write paths:
- Any source code
- Any tests
- Any `.planning/` approval markers
- Any `docs/plans/` files outside the allowed path
- Any files owned by the other swarms:
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-2-capability-gap-map.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-3-plan-review-drift.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-4-execution-readiness-partition.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-5-learning-transfer.md`

Required work:
1. Inspect the current git state of the workspace-hub root and each tier-1 nested repo if present.
2. Identify dirty worktrees, unpushed commits, stale branches, detached worktrees, or sync blockers.
3. Inspect current GitHub issue workflow labels where possible: `status:plan-review`, `status:plan-approved`, `status:blocked`, `status:in-progress`.
4. Identify issues that appear workflow-risky: closed without transactional cleanup evidence, status labels inconsistent with comments, approved labels without local approval markers where required, stale plan-review items, implementation-looking work without approval evidence.
5. Produce a concise report with repo-by-repo state table, workflow gate risks, recommended no-code next actions, exact follow-up GitHub issue candidates if needed, and blockers requiring user decision.

Verification:
- Include exact commands run.
- Include evidence snippets, not vague summaries.
- If a repo is unavailable or not cloned, state that explicitly.

Final output:
Return only:
1. Artifact path written
2. Top 5 workflow risks
3. Repos clean/synced vs dirty/blocked
4. Issues needing operator attention
5. Anything unsafe to automate
