# Tool-budget and remote-ref race closeout pattern

Use this reference when an implementation is already committed and verified but closeout is at risk of being skipped because the session is near context/tool-call limits or a git/GitHub race occurs.

## Pattern

1. **Closeout evidence before optional polish**
   - Once the deliverable commit is pushed or otherwise verified on `origin/main`, immediately post the GitHub issue evidence comment.
   - Close the issue in a separate command after the comment lands.
   - Do not delay issue evidence comments for optional cleanup, broad worktree hygiene, or extra report polish.

2. **Verify issue state after closure**
   - Confirm the issue is `CLOSED`.
   - Confirm the last/recent comment contains the closeout evidence.
   - Move stale workflow labels such as `status:plan-approved` to a terminal label such as `status:done` when the repo label set supports it.

3. **Handle GitHub remote ref-lock races safely**
   - A push can emit a remote rejection like `cannot lock ref ... is at <new_sha> but expected <old_sha>` even when the remote actually accepted the commit.
   - Do not blindly retry and risk churn. First verify:
     - `git ls-remote origin refs/heads/main`
     - `git fetch origin main`
     - `git rev-parse HEAD`
     - `git rev-parse origin/main`
   - If `HEAD == origin/main == intended_sha`, record the push as verified despite the transient ref-lock error.
   - If remote differs, then resolve as a normal divergence/serialization problem before claiming push success.

## Minimal closeout evidence block

Include:
- Result: landed / already done / blocked
- Commit(s) and pushed-head evidence
- Key files/artifacts
- Validation commands and results
- Review verdicts, if required by workflow
- Residual dirty state explicitly scoped as unrelated runtime/session state, if present
