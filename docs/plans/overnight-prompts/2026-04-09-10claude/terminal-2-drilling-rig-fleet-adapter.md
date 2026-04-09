We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2062 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2062: feat(naval-arch): drilling rig fleet adapter — 2,210 rigs into hull form validation
- Labels: enhancement, cat:engineering, domain:code-promotion, agent:claude

Source issue body:
## Context
#1859 built a construction vessel adapter (`normalize_fleet_record` / `register_fleet_vessels`). The same pattern should extend to drilling rigs.

worldenergydata has `drilling_rigs.csv` with **2,210 rigs** from BSEE WAR data, including hull type (drillship, semi-submersible, jack-up) and water depth capability.

## What Needs Doing
1. **Extend or add a drilling rig adapter** in `ship_data.py` that normalizes drilling rig records from `drilling_rigs.csv` into the `_SHIPS` registry shape
2. **Map rig types to hull forms**: drillship → monohull, semi-submersible → twin-hull, jack-up → barge
3. **Feed registered rigs into `hull_form.py`** for form coefficient validation:
   - Block coefficient (Cb) estimation from hull type
   - Midship coefficient (Cm) from hull type
   - Prismatic coefficient (Cp) from Cb/Cm
4. **Validate** that estimated hull form coefficients fall within reasonable ranges for each rig type

## Data Available
- `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` — 2,210 records
- `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_rig.py` — dataclass model
- `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` — form coefficients

## Acceptance Criteria
- Drilling rig adapter normalizes at least the major fields (name, LOA, beam, draft, rig type)
- Hull form coefficients estimated for drillships and semi-subs fall within published ranges
- Tests cover at least 3 rig types with sanity checks

## Depends On
- #1859 (vessel fleet adapter pattern) — DONE
- #1319 (hull form parametric design)

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- digitalmodel/src/digitalmodel/naval_architecture/, digitalmodel/tests/naval_architecture/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md`:
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
