# Provider-unavailable plan-review holding pattern

Use this reference when an engineering-critical plan is otherwise ready for user visibility but Codex/Claude/Gemini review fanout returns only provider/tooling failures.

## Session pattern captured
- Plan-review fanout produced `UNAVAILABLE` artifacts for every provider.
- The plan still needed to be surfaced to the user with `status:plan-review` for human review.
- Local git operations became unreliable because provider/hook processes spawned stuck `git status`/commit work.
- A docs-only GitHub API commit was used to publish the final plan/index/review artifacts, then remote content and issue labels were verified via GitHub API before commenting.

## Required handling
1. Treat all-`UNAVAILABLE` fanout as **no substantive review signal**.
2. Do not claim automated review passed or that no MAJOR findings remain.
3. Keep `status:plan-review` only as a visible holding state: posted for user review, implementation blocked.
4. Add a governance review artifact that names the actual failures and states the evidence gap.
5. Patch the plan/index/comment so they agree on status semantics:
   - ready for user review as a blocked packet,
   - not implementation-approved,
   - automated review retry or explicit user override still needed.
6. If local git is blocked by stuck provider processes, inspect narrowly (`ps`, lock files, `lsof`) and avoid broad `git status` loops. For docs-only plan artifact publication, GitHub API commit/update is acceptable if followed by API verification of remote file contents and issue labels/comments.

## Verification checklist
- Remote HEAD contains the intended plan/index/review artifacts.
- The issue has `status:plan-review`.
- The issue comment links the plan and states provider review was unavailable.
- The comment states implementation remains blocked until explicit user approval / `status:plan-approved`.
