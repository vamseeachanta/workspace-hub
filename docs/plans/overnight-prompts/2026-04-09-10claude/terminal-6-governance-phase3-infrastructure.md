We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2057 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2057: Session governance Phase 3: restore lost session infrastructure
- Labels: enhancement, priority:medium, cat:ai-orchestration, agent:claude

Source issue body:
## Context

#1839 identified several pieces of session infrastructure that were lost during the GSD migration or never built. Phase 1 delivered the checkpoint model. Phase 2 (separate issue) wires runtime enforcement. This issue covers rebuilding the lost skills.

## Lost Infrastructure to Restore

### 1. session-start-routine skill
- **Lost during**: GSD migration cleanup
- **Purpose**: Pre-flight checks at session start — load context, check prior state, validate env, check for in-flight work from other terminals
- **Deliverable**: `.claude/skills/` skill file with checklist

### 2. session-corpus-audit skill
- **Never built**
- **Purpose**: Analyze session quality trends — identify high-churn patterns, report waste, flag sessions >500 tool calls
- **Deliverable**: Skill that reads session signals from `.claude/state/session-signals/` and produces a quality report

### 3. comprehensive-learning → skills tree
- **Status**: Runs via cron (`scripts/cron/`) but invisible to skill discovery
- **Purpose**: Extract and compound learnings across sessions
- **Deliverable**: Register in skills tree so it's discoverable via `/learn-extended` or similar

### 4. cross-review-policy skill
- **Status**: Policy exists as doc (`docs/standards/AI_REVIEW_ROUTING_POLICY.md`) but not as actionable skill
- **Deliverable**: Skill that enforces review routing (which agent reviews which agent's work)

### Tests
- Each skill should have at least a smoke test verifying it loads and has required sections

### References
- Governance doc: `docs/governance/SESSION-GOVERNANCE.md` (Phase 3 section)
- Session signals: `.claude/state/session-signals/`
- Review routing policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Parent: #1839

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- docs/governance/, scripts/workflow/, tests/work-queue/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md`:
1. Title and issue metadata
2. Current-state findings
   - files/modules already present
   - tests already present
   - latest relevant commits if discoverable
3. Remaining implementation delta
   - exact missing behaviors
   - exact file paths that should change when implementation is approved
4. TDD-first execution plan
   - failing tests to add first
   - implementation steps second
   - verification commands
5. Risk/blocker analysis
   - plan-gate blockers
   - data/source dependencies
   - likely merge/contention concerns
6. Ready-to-execute prompt
   - a self-contained future Claude implementation prompt for this issue only
   - include acceptance criteria and cross-review requirements
7. Final recommendation
   - one of: READY AFTER LABEL UPDATE / NEEDS ISSUE REFINEMENT / ALREADY MOSTLY DONE

Verification before finish:
- confirm the dossier file exists
- include at least 3 concrete repo file paths in the analysis
- include at least 3 concrete verification commands
- include a clear recommendation line at the end
