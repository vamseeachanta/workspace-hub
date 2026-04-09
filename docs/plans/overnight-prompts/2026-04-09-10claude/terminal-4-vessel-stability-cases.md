We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2059 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2059: feat(naval-arch): real vessel stability test cases from fleet data (Sleipnir, Thialf, Balder)
- Labels: enhancement, cat:engineering, domain:code-promotion, agent:claude

Source issue body:
## Context
#1859 wired worldenergydata vessel-fleet records into the naval_architecture `_SHIPS` registry via `register_fleet_vessels()`. The adapter is live (commits `81da910a`, `197fc901`).

**Next step**: Use the 17 registered construction vessels as real-world test cases for stability calculations.

## What Needs Doing
1. **Register all 17 construction vessels** from `construction_vessels.csv` via `register_fleet_vessels()` in a test fixture
2. **Estimate stability parameters** for semi-submersible vessels (Sleipnir, Thialf, Balder):
   - KB ≈ T/2 (box approximation)
   - BM ≈ B²/(12*T) (rectangular waterplane)
   - KG — use literature/estimated values or parametric formulas
3. **Run floating platform stability checks** (`floating_platform_stability.check_intact_stability`) against `PlatformType.SEMISUB` criteria
4. **Validate** that GZ curves and area criteria produce physically reasonable results for known vessel geometries

## Integration Points
- `ship_data.register_fleet_vessels()` — already implemented (#1859)
- `floating_platform_stability.compute_gm()`, `compute_gz_curve()`, `check_intact_stability()` — already implemented (#1850)
- Test file: `tests/naval_architecture/test_vessel_fleet_adapter.py` (extend or new file)

## Acceptance Criteria
- At least 3 real construction vessels produce non-trivial stability results
- Semi-submersible vessels pass/fail IMO criteria as expected
- Tests document assumed vs measured parameters clearly

## Depends On
- #1859 (vessel fleet adapter) — DONE
- #1850 (floating platform stability) — DONE

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- digitalmodel/src/digitalmodel/naval_architecture/, digitalmodel/tests/naval_architecture/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md`:
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
