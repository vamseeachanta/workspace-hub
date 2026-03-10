# WRK-637 Cross-Review — Codex

**Verdict: APPROVE (MINOR findings)**

## Key Findings

### MINOR — `--memory-root` flag required
Glob-based discovery of `~/.claude/projects/*/memory/` is too brittle for cron.
Resolution: Add `--memory-root` arg; fail on ambiguous discovery.

### MINOR — `--check-commands` must be opt-in
Running arbitrary commands from bullets in unattended flows is a risk.
Resolution: `--check-commands` flag; disabled by default for nightly cron.

### MINOR — Test coverage insufficient for file-mutation script
"Minimum 3 PASS" is not a credible gate. Need full unit coverage of mutation logic
plus at least one integration smoke test.
Resolution: Expand to ≥10 tests covering happy-path + edge cases.

### MINOR — `# keep` scope
`# keep` should exempt age eviction ONLY — not done-WRK or path staleness archival.
This is already the design intent; needs explicit test to confirm.

### MINOR — Date math robustness
Missing or malformed dates must degrade to `manual-review`, not crash or silently evict.

### MINOR — Idempotency contract
Zero-change apply must write a zero-change log entry (not silence).

### MINOR — uv invocations
All Python invocations in tests, docs, and integration must use `uv run --no-project python`.

## Overall Assessment
Plan is sound. All findings are MINOR and absorbed into the plan. No blocking issues.
