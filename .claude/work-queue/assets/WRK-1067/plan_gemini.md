# Gemini Review: REQUEST_CHANGES

## Verdict: REQUEST_CHANGES

### Issues Found
- Objective mismatch: ratchet-only doesn't enforce hard 80% minimum; use max(80, baseline-2)
- --cov=src assumption fails for non-src-layout repos; use repo-owned [tool.coverage.run] source
- Terminal output parsing is brittle; use structured JSON report
- SKIP_COVERAGE=1 needs audit logging with reason

### Suggestions
- Enforce actual >= max(80, baseline_pct - allowed_drop) — hard floor + ratchet
- Use --cov-report=json and parse coverage.json; don't scrape stdout
- Don't hardcode --cov=src; rely on each repo's [tool.coverage.run] source config
- Require SKIP_COVERAGE_REASON=... and log to artifact
