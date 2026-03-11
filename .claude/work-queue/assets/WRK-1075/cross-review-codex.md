# Cross-Review — Codex — WRK-1075 Plan (v1)

**Verdict: REQUEST_CHANGES**

## Summary
The overall direction is reasonable, but the plan is not yet execution-safe. The biggest
gaps are around repo-local vs hub-level execution boundaries, CI trigger design, and an
insufficient test strategy for mkdocstrings/griffe behavior on real repos.

## Issues Found
- Phase ordering: should pilot one real repo before rolling to all 5
- AC#4 (broken imports fail) underspecified — griffe needs explicit config to fail reliably
- Hub script vs repo-local CI boundary unclear
- CI strategy inconsistent (extend some, new for others) without rationale
- `uv add --dev` may miss import-time deps/extras
- `--serve` AC has no testable verification path (hangs in CI)
- Integration test too narrow (assetutilities only; digitalmodel is highest risk)
- AC set incomplete: missing nav exposure, output path, CI artifact behavior
- No rollback/failure policy for repos with existing docstring problems
- Cross-review as AC #6 is process evidence, not product behavior

## Resolution
Plan v2 addresses all issues. See revised plan in WRK-1075.md.
