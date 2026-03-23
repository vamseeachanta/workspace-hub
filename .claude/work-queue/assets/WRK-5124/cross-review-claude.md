### Verdict: REQUEST_CHANGES

### Summary
The plan addresses the right problem but has two correctness gaps: the non-timeout checker failure path is missing from the shown code, and the uv readiness check in submit-to-gemini.sh can itself hang — reintroducing the exact stall this plan aims to fix.

### Issues Found
- [P2] Important: Non-timeout checker failures unhandled in shown code — after the `if [[ $stage5_exit -eq 124 ]]` block, the snippet ends. There is no shown handling for other non-zero exit codes (e.g., checker returns 1). Test scenario #6 ('Stage 5 checker returns non-zero quickly — distinct from timeout') has no corresponding implementation. The plan must show how non-124 non-zero exits are handled (exit 2? propagate the code? log and continue?).
- [P2] Important: `check_uv_readiness()` in submit-to-gemini.sh runs `uv run --no-project python -c 'print(1)'` with no timeout. If uv is installed but broken in a *hanging* way (the exact failure mode this WRK addresses), this readiness check will itself hang indefinitely. Wrap it in `timeout 10s uv run ...` or equivalent.
- [P2] Important: `timeout` missing on macOS is acknowledged in Risk but has no mitigation strategy. Since this fix targets a cross-provider stall that already hit Gemini (exit 124), and contributors may run on macOS, the plan should specify a fallback (e.g., check for `gtimeout`, or skip the timeout wrapper with a warning, rather than hard-failing via exit 2 and blocking macOS users entirely).

### Suggestions
- Add an explicit else-branch after the timeout check that handles non-zero `stage5_exit`: log the checker's stderr (`$stage5_output`), and exit with a distinct code or propagate the checker's exit code.
- Wrap the uv readiness probe in `timeout 10s` to prevent the readiness check itself from becoming a hang vector: `timeout 10s uv run --no-project python -c 'print(1)'`.
- For macOS compatibility, add a `timeout` resolution block: prefer `timeout`, fall back to `gtimeout`, and if neither exists either skip the timeout wrapper with a logged warning or point users to `brew install coreutils`.

### Questions for Author
- What is the intended behavior when the Stage 5 checker exits non-zero but doesn't timeout — should cross-review.sh block the review (exit 2), or log a warning and continue?
- Is macOS a supported development/CI platform for this workflow? If so, the hard exit on missing `timeout` needs a fallback path.
