# WRK-5124 AC-Test Matrix

| AC | Description | Result | Evidence |
|----|-------------|--------|----------|
| 1 | cross-review.sh fails fast (exit 2) when uv missing | PASS | `command -v uv` check present before gate |
| 2 | cross-review.sh falls back to gtimeout on macOS | PASS | `gtimeout` fallback chain in timeout resolution |
| 3 | cross-review.sh uses validated timeout from config (default 30s) | PASS | `checker_timeout` read with integer regex validation |
| 4 | cross-review.sh exits 2 with TIMED OUT on timeout (124) | PASS | `stage5_exit -eq 124` handling with diagnostic message |
| 5 | cross-review.sh preserves checker exit 1 vs exit 2+ distinctly | PASS | Separate branches for exit 1 (predicate) and other (infra) |
| 6 | submit-to-gemini.sh checks uv readiness with timeout-wrapped probe | PASS | `check_uv_readiness()` with `timeout 10s` / `gtimeout 10s` |
| 7 | Happy path unchanged for all three providers | PASS | No changes to success path logic; only error handling added |
