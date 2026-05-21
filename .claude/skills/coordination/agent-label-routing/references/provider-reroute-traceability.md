# Provider Reroute Traceability Pattern

Use this when a GitHub issue has already been routed to an `agent:` lane, but the selected provider cannot complete the work in the current execution environment or quota state.

## Goal

Keep the work moving without losing auditability. A reroute should leave enough evidence for another operator to reconstruct:

- which provider was attempted,
- what prompt/worktree/log was used,
- what failed,
- why the replacement provider was selected,
- what must be verified before claiming progress.

## Required sequence

1. **Capture evidence before changing labels**
   - Worktree path
   - Branch name
   - Prompt path, usually `.planning/quick/<issue>-<provider>-prompt.md`
   - Process/session ID if launched through Hermes
   - Log path and concise failure excerpt

2. **Comment on the issue**

   Recommended body shape:

   ```markdown
   Rerouting agent lane.

   Attempted provider: Codex
   Worktree: /mnt/local-analysis/agent-worktrees/<repo>-issue-<n>-<slug>
   Prompt: .planning/quick/<issue>-codex-prompt.md
   Log: logs/<provider>-issue-<n>.log
   Failure evidence: <short excerpt; avoid huge logs>

   Decision: rerouting to Claude because this lane needs local write/test execution and the current provider run did not produce verifiable local changes.
   Next verification: inspect replacement diff, run targeted tests, then perform code-stage review before integration.
   ```

3. **Change only routing labels**

   ```bash
   gh issue edit <n> --remove-label "agent:codex" --add-label "agent:claude"
   ```

   Do not add or remove `status:*` labels unless the workflow gate changed. Rerouting provider ownership is not plan approval and not closeout.

4. **Launch replacement with explicit inherited context**
   - Either reuse the existing worktree if it is clean enough, or create a new worktree and say why.
   - Point the replacement prompt to prior artifacts and failure evidence.
   - Keep allowed paths narrow.

5. **Use constrained review-only fallback when available**
   - If a provider cannot perform local shell/write operations but can still inspect a GitHub issue/PR/repo through a connector, use it only for read-only adversarial review or planning critique.
   - Record the limitation in the issue comment/review artifact: `scope: GitHub-connector/read-only; no local test execution verified by this provider`.
   - Do not count connector-only review as implementation evidence. Local diff/test verification still belongs to the orchestrator or a write-capable replacement lane.

6. **Verify replacement output independently**
   - Inspect `git status` and diff.
   - Run the targeted tests named in the approved plan.
   - Check that result/report artifacts exist and match the issue scope.
   - Only then update the issue with progress or closeout evidence.

## Pitfalls

- Do not encode a provider-specific transient failure as a durable negative capability claim. Capture the reroute procedure, not “provider X cannot do Y.”
- Do not silently switch providers; labels and issue comments are the audit trail.
- Do not let connector-only/read-only review evidence masquerade as local implementation or test evidence; label it as review scope and verify implementation separately.
- Do not let a failed first provider contaminate final evidence. Final status must be based on independently verified replacement output.
- Do not start downstream result/output-layer issues until upstream data-contract issues have landed or the dependency is explicitly mocked in the approved plan.
