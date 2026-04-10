# Claude Stage 4 — Next Waves (2026-04-09)

Generated from:
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-5-next-wave-prompts.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-4-priority-matrix.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-1-operator-runbook.md

## Dispatch Plan

Wave 2 — parallel Claude implementation (3 terminals)
- T1: #2063 drilling riser adapter
- T2: #2059 vessel stability test cases
- T3: #2054 decline curve economics

Wave 3 — sequential Claude implementation after decision
- T4: #2060 timeline benchmarks
- Precondition: decide whether benchmarks.py may grow to ~700 lines or timeline.py should be extracted.

## Prompt Files

Wave 2:
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-1-drilling-riser-adapter.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-2-vessel-stability-tests.md
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-3-decline-curve-economics.md

Wave 3:
- docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave3/terminal-1-timeline-benchmarks.md

## Git Contention Map

Terminal 1 writes:
- digitalmodel/src/digitalmodel/drilling_riser/
- digitalmodel/tests/drilling_riser/

Terminal 2 writes:
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
- digitalmodel/tests/naval_architecture/conftest.py

Terminal 3 writes:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/tests/field_development/test_economics.py

Wave 3 terminal writes:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py or timeline.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py
- worldenergydata/subseaiq/analytics/normalize.py

Zero same-file overlap in Wave 2.
Wave 3 must run after Wave 2 because it may touch field_development shared surfaces.

## Cross-Review Policy

Codex cross-review required after each engineering implementation:
- #2063 unit conversion logic
- #2059 tolerance ranges and parametric estimates
- #2054 Arps decline formulas and backward compatibility
- #2060 percentile logic and alias assumptions

## Launch Pattern

Example:
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave2/terminal-1-drilling-riser-adapter.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee logs/claude-stage4-wave2-t1.log

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
