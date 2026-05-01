# Post-Compaction Merge Verification

Use when a merge/push occurred before context compaction or tool output was truncated, and the next agent must produce a final report.

## Verification commands

Run fresh checks from the involved checkouts instead of relying on summarized/truncated output:

```bash
git -C /mnt/local-analysis/workspace-hub fetch origin main --prune
git -C /mnt/local-analysis/workspace-hub log origin/main --oneline --decorate -12
git -C /mnt/local-analysis/worktrees/<integration-worktree> status --short --branch
git -C /mnt/local-analysis/worktrees/<integration-worktree> log --oneline --decorate -10
git -C /mnt/local-analysis/workspace-hub status --short --branch | sed -n '1,80p'
```

If any legal/security check previously exited nonzero or its output was truncated, inspect the saved artifact and/or rerun in the clean integration worktree before claiming success:

```bash
cat /tmp/<legal-scan>.json
cd /mnt/local-analysis/worktrees/<integration-worktree>
git diff --check
scripts/legal/legal-sanity-scan.sh --diff-only --json
```

## Reporting rules

- Report exact `origin/main` hash and landed commit list from fresh `git log`, not memory.
- Distinguish the clean integration worktree from the dirty original checkout.
- If the original checkout is dirty/behind, state that it was preserved intentionally; do not reset/clean it without explicit approval.
- If validation was rerun after conflict resolution, include the exact command and pass/fail counts.
- If any check remains ambiguous, label it as a caveat instead of implying it passed.

## Pitfalls

- A wrapper command can exit `0` while the underlying cherry-pick or validation wrote conflict/failure output to a log; inspect the log when later actions imply conflicts occurred.
- API transcript truncation can hide branch status, issue states, cron status, and legal-scan failures; final reports need fresh verification.
- Generated artifacts from tests/hooks, such as coverage JSON, should be restored before push unless intentionally in scope.