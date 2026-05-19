# Issue Tree Exit Closeout

Use when ending a session after creating, planning, reviewing, approving, implementing, or partially closing a linked GitHub issue tree.

## Trigger

The user asks for closeout / exit status, or the session is ending with a multi-issue tree where some children are closed and others remain gated (for example `status:plan-review`).

## Required closeout shape

Produce a transactional status that separates finished work from restart points:

1. Current state by issue:
   - umbrella / parent issue state;
   - each child issue state;
   - gate label, especially `status:plan-review` vs `status:plan-approved`;
   - whether implementation is blocked pending user approval.
2. Evidence:
   - issue URLs grounded by `gh issue view` during the session;
   - plan/report/handoff artifact paths;
   - commit SHAs and pushed branch;
   - validation commands and results.
3. Remaining restart points:
   - exact issue numbers to resume;
   - required user decision or approval;
   - preserved worktrees or unrelated local state.
4. Clean-state verification:
   - `HEAD`, `origin/main`, and remote `refs/heads/main` agree;
   - ahead/behind is `0 0` when claiming sync;
   - tracked worktree dirty count is zero;
   - unrelated worktrees are listed and explicitly preserved, not silently removed.
5. Push-warning reconciliation:
   - if `git push` emits a GitHub-side ref-lock / cannot-lock-ref warning but exits ambiguously or the remote may still have accepted the object, immediately re-query `git ls-remote origin refs/heads/<branch>`, `git rev-parse HEAD`, `git rev-parse origin/<branch>` after `git fetch`, and `git rev-list --left-right --count HEAD...origin/<branch>`;
   - treat the warning as benign only when local `HEAD`, fetched tracking ref, and remote ref all match and ahead/behind is `0 0`;
   - include the warning and verification evidence in the handoff instead of claiming a clean push from the warning alone.

## Handoff artifact pattern

For complex issue trees, create durable markdown handoffs under `docs/session-handoffs/` before the final response. Prefer one handoff per separable restart domain, e.g. architecture/governance vs machine/connectivity operations.

Each handoff should include:

- issue list with state/gate label;
- artifacts created/updated;
- validation commands already run;
- exact blocked decision or next checkpoint;
- explicit non-actions and preserved state.

## Pitfalls

- Do not report “done” for the whole tree when only the parent or one child is closed. Say which issues remain open and why.
- Do not treat `status:plan-review` as approval. It is a user-review queue, not implementation permission.
- Do not use a local commit hash alone as sync evidence. Verify push and remote ref state.
- Do not sweep unrelated dirty files or unrelated worktrees into the closeout commit. Preserve and name them.
- Do not perform external sends/actions at exit unless the user explicitly requested them; state that no external send/action occurred when relevant.
