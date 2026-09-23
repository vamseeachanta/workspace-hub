# Adversarial plan review — #3424 skill lifecycle r6

Provider: Codex parallel reviewer

Verdict: MAJOR

## Findings

1. The plan assumed a `PLAN_APPROVAL_OWNERS` repository variable that does not exist; bootstrap would fail before authority evaluation.
2. The bootstrap validated the remote PR but did not require the local branch/HEAD or staged/unstaged state to equal that approved head.
3. The planned owned `.git/index.lock` blocked the subsequent `git write-tree` call; the transaction self-deadlocked its own verifier.
4. Removing `.planning/plan-approved/3424.md` violated the mandatory issue-planning and provider-dispatch contracts, which still require both label and marker.

## Required disposition

- Freeze a reviewed owner allowlist or establish the missing protected repository variable.
- Bind local branch/HEAD/index/worktree to the approved PR head before writes.
- Use only read-only index verification while the owned lock is held and add a lock-held integration test.
- Restore and verify a user-created approval marker or separately migrate every consumer.

No files were edited by the reviewer.
