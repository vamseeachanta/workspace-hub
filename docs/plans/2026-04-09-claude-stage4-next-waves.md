# Claude Stage 4 — Next Waves (2026-04-09)

Generated from:
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-5-next-wave-prompts.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-4-priority-matrix.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-1-operator-runbook.md
- docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md

## Dispatch Plan

Wave 2 — parallel Claude implementation (3 terminals)
- T1: #2063 drilling riser adapter
- T2: #2059 vessel stability test cases
- T3: #2054 decline curve economics

Wave 3 — sequential Claude implementation after decision
- T4: #2060 timeline benchmarks
- Precondition: decide whether benchmarks.py may grow to ~700 lines or timeline.py should be extracted.

Wave 4 — next Claude wave after plan gates clear
- T1: #2058 subsea architecture patterns
- T2: #2062 drilling rig fleet adapter
- Preconditions:
  - #2058 must already be human-reviewed and labeled `status:plan-approved`
  - #2058 may start only after #2060 lands and no other session is editing `benchmarks.py` / `SubseaProject`
  - #2062 title/body must be refined to the ~138-rig v1 scope, then human-reviewed and labeled `status:plan-approved`

## Prompt Files

Wave 2:
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-1-drilling-riser-adapter.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-2-vessel-stability-tests.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-3-decline-curve-economics.md

Wave 3:
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave3/terminal-1-timeline-benchmarks.md

Wave 4:
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave4/terminal-1-architecture-patterns.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave4/terminal-2-drilling-rig-fleet-adapter.md

## Git Contention Map

Wave 2 terminal 1 writes:
- digitalmodel/src/digitalmodel/drilling_riser/
- digitalmodel/tests/drilling_riser/

Wave 2 terminal 2 writes:
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
- digitalmodel/tests/naval_architecture/conftest.py

Wave 2 terminal 3 writes:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/tests/field_development/test_economics.py

Wave 3 terminal writes:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py or timeline.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py
- worldenergydata/subseaiq/analytics/normalize.py

Wave 4 terminal 1 writes:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/architecture_patterns.py
- digitalmodel/tests/field_development/test_benchmarks.py
- digitalmodel/tests/field_development/test_architecture_patterns.py
- worldenergydata/subseaiq/analytics/normalize.py

Wave 4 terminal 2 writes:
- digitalmodel/src/digitalmodel/naval_architecture/hull_form.py
- digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
- digitalmodel/src/digitalmodel/naval_architecture/__init__.py
- digitalmodel/tests/naval_architecture/test_hull_form.py
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py

Zero same-file overlap in Wave 2.
Wave 3 must run after Wave 2 because it may touch field_development shared surfaces.
Wave 4 T1 and T2 are parallel-safe with each other, but T1 must not start until Wave 3 is merged or otherwise no longer contending on `benchmarks.py`.

## Cross-Review Policy

Codex cross-review required after each engineering implementation:
- #2063 unit conversion logic
- #2059 tolerance ranges and parametric estimates
- #2054 Arps decline formulas and backward compatibility
- #2060 percentile logic and alias assumptions
- #2058 architecture analytics, normalization aliases, and benchmark dataclass extensions
- #2062 rig hull coefficient heuristics and draft-estimation logic

## Launch Pattern

Example:
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave4/terminal-1-architecture-patterns.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee logs/claude-stage4-wave4-t1.log

## What you’ll have after Wave 2

From T1:
- drilling riser CSV adapter
- integration tests for registration and weight calculations

From T2:
- real-vessel stability regression coverage for Sleipnir, Thialf, Balder
- explicit assumed-vs-measured test notes

From T3:
- decline curve support in economics cashflow modeling
- regression coverage for enum, validation, and backward compatibility

From Wave 3:
- timeline benchmark functions
- timeline parsing support in SubseaProject
- normalization aliases for first scrape ingestion

From Wave 4:
- subsea architecture analytics module plus extended normalized flowline/layout fields (#2058)
- drilling rig fleet adapter with realistic ~138-rig v1 throughput and hull-form heuristics (#2062)
