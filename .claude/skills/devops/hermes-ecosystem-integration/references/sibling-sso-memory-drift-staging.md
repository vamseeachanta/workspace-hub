# Sibling SSoT Memory Drift Staging

Use this reference when executing sibling-repo SSoT work that modifies Hermes config, provider symlinks, registry topology, or memory bridge contracts.

## Why this matters

During cross-repo SSoT implementation, generated or bridge-synced `.claude/memory/**` files can appear in the same dirty worktree as real implementation files. Those memory changes may be unrelated to the approved issue and can even point canonical memory paths at an agent worktree, making the worktree look like the new source of truth.

## Pre-stage checklist

Before staging a sibling SSoT fix:

1. Inspect config/script/test/docs diffs separately from `.claude/memory/**` diffs.
2. Treat memory diffs as suspect if they:
   - replace canonical workspace-hub paths with `/mnt/local-analysis/agent-worktrees/...`,
   - revert current privacy or public/private routing language,
   - look like bulk bridge output rather than a deliberate contract edit,
   - update many topic files without a matching acceptance criterion.
3. Stage only issue-owned surfaces first: registry, Hermes template, sync/check/repair scripts, tests, and required docs.
4. Run the memory drift validator after implementation validation, before commit:
   - `bash scripts/memory/check-memory-drift.sh`
5. Commit memory changes only when the approved issue explicitly requires them and the drift check is green.

## Closeout wording

In GitHub closeout for SSoT issues, include one line confirming either:

- `Memory files: not touched/staged; drift check PASS`, or
- `Memory files: intentionally changed for <reason>; drift check PASS`.

Do not say workspace-hub is the SSoT for memory unless the bridge state was actually verified.