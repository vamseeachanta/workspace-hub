We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2060 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2060: feat(field-dev): project timeline benchmarks from SubseaIQ milestone data
- Labels: enhancement, cat:engineering, agent:claude

Source issue body:
## Context
Follow-up to #1861 (scaffold commit `aaf90c8e`). The benchmark bridge handles static project attributes. This issue adds temporal/schedule analysis for project planning.

## Scope
- [ ] Add timeline fields to `SubseaProject`: year_concept, year_feed, year_fid, year_first_oil
- [ ] Compute Concept→FEED→FID→First Oil duration statistics
- [ ] Duration statistics by concept type and project complexity
- [ ] Project schedule probability distributions (P10/P50/P90 durations)
- [ ] Extend normalizer with timeline field aliases from SubseaIQ

## Target Files
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (extend dataclass + add timeline stats)
- `digitalmodel/tests/field_development/test_benchmarks.py` (extend)
- `worldenergydata/subseaiq/analytics/normalize.py` (add timeline field aliases)

## Depends On
- #1861 (scaffold — done)
- SubseaIQ scraping with milestone date fields

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- digitalmodel/src/digitalmodel/field_development/, digitalmodel/tests/field_development/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md`:
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
