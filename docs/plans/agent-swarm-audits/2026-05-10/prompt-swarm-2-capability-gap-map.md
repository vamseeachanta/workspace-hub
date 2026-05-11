# /goal Swarm 2 — Tier-1 capability gap + mission alignment map

Build a tier-1 repo capability gap and mission-alignment map for the workspace-hub ecosystem.

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
- This is planning/research-only.
- Do not implement code changes.
- Do not edit source code, tests, config, or GitHub labels.
- Do not create or close issues unless explicitly instructed later by the operator.
- Respect the plan-gated workflow. Your output should prepare future issue planning, not bypass it.

Allowed write path:
- `docs/plans/agent-swarm-audits/2026-05-10/swarm-2-capability-gap-map.md`

Forbidden write paths:
- Any source code
- Any tests
- Any `.planning/` approval markers
- Any files owned by the other swarms:
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-1-live-state-gate-audit.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-3-plan-review-drift.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-4-execution-readiness-partition.md`
  - `docs/plans/agent-swarm-audits/2026-05-10/swarm-5-learning-transfer.md`

Authoritative context to inspect first:
- `AGENTS.md`
- `docs/`
- `docs/standards/`
- `docs/plans/`
- repo README files
- repo mission or architecture docs if present
- existing issue plans and handoffs
- relevant skills under `.claude/skills/` if they describe repo roles

Required work:
1. For each tier-1 repo, identify stated mission, current capability areas, implied ecosystem role, missing/weak capability areas, and stale/missing docs that block retrieval or agent execution.
2. Build a matrix with columns: Repo, Mission / intended role, Current evidence, Capability gaps, Documentation gaps, Execution-readiness gaps, Recommended follow-up issue type.
3. Separate findings into general ecosystem gaps, per-repo gaps, per-domain gaps, planning-needed gaps, and approval-drift risks.
4. Recommend 5-10 future GitHub issue candidates, but do not create them.
5. Include exact file evidence for every material claim.

Verification:
- Use live repo files, not assumptions.
- If a repo is not present locally, mark it unavailable.
- Do not invent repo missions without evidence.

Final output:
Return only:
1. Artifact path written
2. Highest-impact 5 gaps
3. Recommended issue candidates
4. Repos with insufficient mission evidence
5. Suggested next swarm/agent action
