# Gemini Cross-Review: WRK-1067 Plan

## Verdict: REQUEST_CHANGES (resolved in revised plan)

### Summary
Plan doesn't satisfy hard 80% minimum objective; uses brittle terminal scraping; --cov=src assumption fails.

### Issues Found
- Ratchet-only doesn't enforce hard 80% minimum per WRK objective
- --cov=src harness assumption fails for non-src-layout repos
- Terminal output parsing brittle
- SKIP_COVERAGE=1 needs audit logging

### Resolution in revised plan
- Enforce actual >= max(80, baseline_pct - 2) — hard floor + ratchet
- Removed --cov=src from harness; rely on each repo's [tool.coverage.run] source
- Use --cov-report=json structured output
- Changed to SKIP_COVERAGE_REASON=... with logging
