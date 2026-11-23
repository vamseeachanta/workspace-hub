Strict canonical-doc rewrite executed for #2408 and follow-up issue created for provider-entrypoint normalization.

New follow-up issue:
- #2421 — normalize workspace-hub provider entrypoint surfaces

Latest review lane status for narrowed #2408:
- Codex rerun did not yield a clean persisted final verdict artifact in `review-2408-codex-r5.out` (empty output file after sandbox issues)
- Gemini rerun failed before substantive review with tool/runtime issues (`run_shell_command` unavailable after agent-loading warnings)

Operational conclusion:
- this rerun does NOT provide clean approval evidence
- the narrowed plan direction is still the recommended direction, but the current provider review artifacts are incomplete / tooling-degraded

Recommendation:
1. keep #2408 out of `status:plan-review` for the moment
2. treat #2421 as the separate normalization lane
3. when ready, rerun a fresh clean cross-provider review for #2408 after stabilizing the review tooling path
