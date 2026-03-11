### Verdict: REQUEST_CHANGES

### Summary
The plan is well-scoped and technically sound for a Route B item. The three deliverables are coherent and the TDD coverage hits the main paths. However, two meaningful gaps need addressing before implementation: the `|| true` suppression masks non-data failures silently, and the test suite lacks a malformed-JSONL case that is likely to occur in real usage.

### Issues Found
- [P2] Important: `|| true` in close-item.sh suppresses ALL non-zero exits, not just 'no data found'. A Python import error, missing dependency, or broken script would silently pass. The intended guard is only for the 'no data for this WRK' case. Consider catching only exit code 1 (the defined 'no data' exit) or logging stderr even when suppressing the exit code.
- [P2] Important: No test covers malformed/corrupt JSON lines in cost-tracking.jsonl (e.g., a truncated write mid-session). Real JSONL files accumulate bad lines. The loader should skip-and-warn on parse errors; without a test this is likely to be an unhandled exception in production.
- [P2] Important: pricing.yaml is described as a static extract with no refresh or validation mechanism. Model pricing changes frequently; a stale table will silently under/over-report costs. The plan needs either a staleness warning (compare `updated_at` against a threshold) or a documented manual update procedure as part of the WRK definition-of-done.
- [P3] Minor: T6 covers a missing model key in pricing.yaml but there is no test for pricing.yaml being absent entirely. The script should fail clearly (not with a cryptic KeyError or FileNotFoundError) when the config file is missing.
- [P3] Minor: The cost-tracking.jsonl path is not specified in the plan. If it is hardcoded, the script will break when the file moves. If it is read from a config or environment variable, that dependency should be stated explicitly so tests can use a fixture path cleanly.

### Suggestions
- Replace `|| true` with a targeted check: capture stderr, log it, and only suppress exit code 1. Example: `uv run --no-project python scripts/ai/wrk-cost-report.py "$WRK_ID" 2>&1 || { rc=$?; [ $rc -eq 1 ] && true || echo "[WARN] wrk-cost-report failed (exit $rc)"; }`
- Add T8: JSONL with one valid line, one malformed line, one valid line — assert the two valid entries are aggregated and a warning is emitted for the bad line.
- Add a `--check-pricing-age N` flag (or a startup warning) that prints a notice when `updated_at` in pricing.yaml is older than N days. 30 days is a reasonable default.
- Document the cost-tracking.jsonl path (or config key) in a brief 'Configuration' section of the plan so implementers and test authors have a single source of truth.

### Questions for Author
- What is the expected file size growth rate of cost-tracking.jsonl? If it grows large (e.g., >10 MB over months of sessions), reading the entire file at close time adds latency. Is streaming/tail-read or an index acceptable scope for this WRK, or is that a future item?
- Are all acceptance criteria for WRK-1069 listed in this plan, or only the ones not yet satisfied? The plan notes AC-1 is already done but does not enumerate AC-2, AC-3, etc. — the reviewer cannot confirm completeness without the full AC list.
- Is the pricing.yaml extraction from model-registry.yaml a one-time manual copy, or will a script generate it? If manual, who owns keeping it current, and is that documented in the file header?
