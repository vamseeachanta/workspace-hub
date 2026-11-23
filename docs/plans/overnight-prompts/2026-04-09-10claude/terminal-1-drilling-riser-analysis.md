We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2063 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2063: feat(naval-arch): wire drilling riser components into mooring/riser analysis
- Labels: enhancement, cat:engineering, domain:code-promotion, agent:claude

Source issue body:
## Context
worldenergydata has `drilling_riser_components.csv` with **36 components** (riser joints, BOPs, LMRPs, flex joints) with physical specs (weight, OD, length). These should feed into any existing mooring/riser analysis modules in digitalmodel.

This is part of the #1859 integration roadmap — wiring worldenergydata vessel/equipment data into engineering calculation modules.

## What Needs Doing
1. **Identify target modules** in digitalmodel that perform riser or mooring analysis
2. **Build an adapter** (following the #1859 pattern) that normalizes riser component records into the expected input shape
3. **Create test cases** using real component specs (e.g., 21" marine riser joint, 18-3/4" BOP)
4. **Validate** that riser string weight calculations produce physically reasonable results

## Data Available
- `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` — 36 records
- `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_riser.py` — dataclass model
- `worldenergydata/src/worldenergydata/vessel_fleet/loaders/drilling_riser_loader.py` — loader

## Acceptance Criteria
- Riser component adapter normalizes OD, weight, length into calculation-ready units
- At least one integration test computes riser string weight from real component specs
- Adapter follows the same `normalize_*_record` / `register_*` pattern from #1859

## Depends On
- #1859 (adapter pattern) — DONE

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- digitalmodel/src/digitalmodel/drilling_riser/, digitalmodel/tests/drilling_riser/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md`:
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
