We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2054 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2054: feat(field-dev): add production decline curve to economics cashflow model
- Labels: enhancement, cat:engineering, domain:code-promotion, agent:claude

Source issue body:
## Context
The economics facade (#1858) uses a simplified production profile: flat plateau for 60% of field life, then linear decline to 20%. worldenergydata has proper decline curve models:

- `worldenergydata.bsee.reports.comprehensive.templates.economic_models` — field-level decline
- `worldenergydata.fdas.data.production` — historical production data
- `worldenergydata.reservoir` — OOIP, EUR, Monte Carlo

## What to do
1. Replace `_build_annual_cashflows()` linear decline with exponential/hyperbolic decline curve
2. Accept optional `decline_rate` and `decline_type` (exponential/hyperbolic/harmonic) in `EconomicsInput`
3. Support `reservoir_size_mmbbl` as input to EUR-based decline curve parameterization
4. Fall back to current linear model if no decline parameters provided

## Files
- `digitalmodel/src/digitalmodel/field_development/economics.py` — `_build_annual_cashflows()`
- `worldenergydata/src/worldenergydata/fdas/data/production.py`

## Parent
Part of #1858 epic. Related to #1845 (production profiles).

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- digitalmodel/src/digitalmodel/field_development/, digitalmodel/tests/field_development/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md`:
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
