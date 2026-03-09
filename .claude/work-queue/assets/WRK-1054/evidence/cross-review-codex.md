# WRK-1054 Phase 1 — Codex Review

**Verdict: MINOR (approve after tightening)**

## Issues
1. Repo scope ambiguous (4 vs 5 with ogmanufacturing optional)
2. Parsing only summary line insufficient — process exit code + timeout must be first-class
3. Expected-failure node IDs need storage contract (dedicated file, exact match, no wildcarding)
4. Bash weak fit for structured parsing — allow Python helper for JSONL emission
5. Test strategy too narrow — add fixtures for no-tests, collection-error, timeout, skipped-only

## Suggestions
- Explicit 4-repo scope in v1
- Result tuple: (process_status, parsed_counts, timed_out)
- Store expected failures in dedicated file (one node ID per line)
- Python helper via `uv run --no-project python` for parsing + JSON
- Expand test fixtures to cover all exit-code paths
