### Verdict: MAJOR

### Summary
The new gate still has merge-blocking bypasses around revision binding and a CI integration failure mode.

### Issues Found
- MAJOR: `scripts/workflow/plan_approval_gate_check.py` `fetch_plan_revision_anchor` / `plan_blob_matches_revision` do not verify that `binding.revision_sha` is the PR head commit or even reachable from the current branch. The gate accepts any repository commit that touched the recorded plan path, as long as that commit's plan blob equals the PR head plan blob. That weakens the required binding from 'approved current branch revision' to 'approved some commit with same plan file content', allowing code changes at PR head to move independently of the approved revision. Required fix: verify the bound SHA is the PR head SHA or an ancestor of the PR head using GitHub compare/merge-base semantics, and make the freshness anchor the bound branch revision being approved.
- MAJOR: `.github/workflows/enforcement-gate.yml` now runs `uv run python scripts/workflow/plan_approval_gate_check.py` before the legacy gate and exits on its rc after the legacy gate. When `PLAN_APPROVAL_GATE_ENABLED=1` and admin prereqs are confirmed, any transient GitHub API/GraphQL/contents call failure in the new experimental gate fails the whole existing enforcement job, even though the comment says the legacy hard gate stays active until the new gate is verified as a required status check. This is a CI cutover regression: enabling test rollout immediately makes the new gate blocking. Required fix: either make the variable name/semantics explicitly mean 'blocking enforcement enabled' or add a separate shadow-mode path where the new gate records failure without failing until cutover is complete.

### Suggestions
- Add tests proving a bound revision that is neither head nor ancestor is rejected.
- Add a workflow test for the intended shadow/cutover behavior, including enabled-but-not-blocking versus blocking mode if both are needed.

### Questions for Author
- Is the approved revision intended to be exactly the PR head SHA, or is an ancestor acceptable once the plan file blob is unchanged? The current code implements neither; it accepts unrelated commits with matching plan blobs.
