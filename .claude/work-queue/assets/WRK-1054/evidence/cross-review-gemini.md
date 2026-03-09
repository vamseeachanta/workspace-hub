# WRK-1054 Phase 1 — Gemini Review

**Verdict: REQUEST_CHANGES**

## Issues
1. Bash stdout parsing fragile — plugins, color codes, unexpected errors
2. pytest exit code 5 (no tests collected) not handled
3. Custom expected-failure list duplicates native pytest xfail functionality

## Suggestions
- Rewrite as Python script OR use `--junitxml` for structured output
- Handle all pytest exit codes explicitly
- Use @pytest.mark.xfail decorators instead of external list

## Response
- Keeping bash as orchestrator (thin wrapper), Python helper for parsing
- Expected failures external list approach retained (repos we don't own / live-data test separation)
- pytest xfail inappropriate here — live-data failures are environmental, not design intent
