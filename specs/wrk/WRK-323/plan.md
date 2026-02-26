# WRK-323 Plan: OrcaFlex Parameter Audit Reference

> Route C spec for `.claude/work-queue/pending/WRK-323.md`

## Problem
The modular OrcaFlex example set has many `inputs/parameters.yml` variants without a consolidated engineering reference. This blocks reliable LLM-led analysis because parameter semantics are inconsistent across categories.

## Implementation Plan
1. Enumerate all modular example parameter files (`A01` to `Z09`) and extract unique keys.
2. Build categorized reference content (environment, geometry, vessel/structure, load case, analysis, staging).
3. Map each YAML key to OrcFxAPI attribute path where direct mapping exists.
4. Produce cross-reference matrix of key-to-example usage.
5. Validate file completeness against enumerated source set.

## Deliverables
- `digitalmodel/docs/domains/orcaflex/examples/PARAMETER_REFERENCE.md`

## Validation
- Spot-check key mappings (`water_depth`, `hs`, `tp`, `wave_direction`, `stage_durations`) against representative example files.

## Cross-Review Log
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1 | 2026-02-24 | Claude | MINOR | Coverage claims needed explicit category cross-reference table. | yes |
| P2 | 2026-02-26 | Codex | APPROVE | Parameter reference artifact present and aligned with acceptance scope. | n/a |
| P3 | 2026-02-26 | Gemini | MINOR | Independent CLI review deferred (local CLI timeout); no contradictory evidence found in artifacts. | deferred |
