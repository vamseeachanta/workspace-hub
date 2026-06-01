---
name: memory-bridge-operations
description: "Operate and recover the Hermes-to-repo memory bridge: drift checks, quality gate, bridge commits, push verification, and stash recovery when pre-bridge scripts fail after generating outputs."
tags: [memory, hermes, bridge, quality-gate, git, recovery]
---

# Memory Bridge Operations

Use this skill when syncing Hermes memory into a git-tracked repo memory directory such as `.claude/memory/`, especially for scheduled jobs that must run autonomously and report bridge status.

## Standard Workflow

1. Enter the workspace repo, usually `/mnt/local-analysis/workspace-hub`.
2. Run drift check:
   ```bash
   bash scripts/memory/check-memory-drift.sh
   ```
   - Exit 0: report `No drift — nothing to bridge` and stop.
   - Exit 1: capture the drift/missing-entry count and continue.
3. Run the quality gate with auto-fix:
   ```bash
   bash scripts/memory/pre-bridge-quality.sh --fix
   ```
4. Extract the quality score from `Score: NN/100`.
5. Report updated `.claude/memory/` files and line counts:
   ```bash
   wc -l .claude/memory/agents.md .claude/memory/context.md .claude/memory/claude-auto-memory.md
   find .claude/memory/topics -type f | wc -l
   find .claude/memory/topics -type f -print0 | xargs -0 wc -l | tail -1
   ```
6. Verify drift is resolved:
   ```bash
   bash scripts/memory/check-memory-drift.sh
   ```
7. Verify commit/push:
   ```bash
   git log --oneline -1 --decorate --no-show-signature
   git branch -r --contains HEAD
   ```

## Quality Gate Semantics

- Score `< 50`: abort; do not bridge degenerate memory.
- Score `50-70`: auto-compaction may run before bridging.
- Score `>= 70`: bridge can run directly; `--fix` may still compact files near limits.

## Recovery: pre-bridge stashed valid memory but exited nonzero

Observed pattern:

- `pre-bridge-quality.sh --fix` prints successful bridge generation:
  - `agents.md generated`
  - `context.md regenerated`
  - `claude-auto-memory.md snapshot updated`
  - topic files mirrored
- Then it says `Uncommitted changes detected — stashing before pull...` and creates `stash@{0}: On main: pre-bridge-stash`.
- The script exits nonzero after `nothing added to commit but untracked files present`, because unrelated untracked files prevented its internal commit path even though the bridge outputs are in the stash.

Safe recovery:

```bash
git stash list --date=local | head
git stash show --name-only stash@{0}
git checkout stash@{0} -- .claude/memory
bash scripts/memory/check-memory-drift.sh
git commit -m "chore(memory): bridge Hermes memory" -- .claude/memory
git push
bash scripts/memory/check-memory-drift.sh
```

Important constraints:

- Do **not** apply the whole stash; it may contain unrelated generated state, plans, reports, or other agents' work.
- Restore only `.claude/memory` for the memory bridge job.
- Leave unrelated untracked files untouched and mention them only as context.
- Final report should distinguish initial drift count from final verified drift state.

## Reporting Template

```markdown
Memory bridge completed.

- Initial drift check: <in sync|drift detected>
- Initial missing entries: <N>
- Quality score: <NN>/100
- Bridge result: <completed|aborted|recovered from stash>
- Final drift recheck: <in sync|still drifted>

Files updated / final line counts:
| Path | Lines |
|---|---:|
| `.claude/memory/agents.md` | <N> |
| `.claude/memory/context.md` | <N> |
| `.claude/memory/claude-auto-memory.md` | <N> |
| `.claude/memory/topics/` | <N files, total lines> |

Commit / push:
- Commit: `<hash> <subject>`
- Push: <succeeded|failed>; `<remote>` contains HEAD: <yes|no>
```

## Pitfalls

- The script output may be partially successful even when the final exit code is nonzero; inspect stashes before declaring failure.
- Drift count can increase after compaction because compacted memories may expose entries not represented in repo memory yet; report both initial and final verified states when relevant.
- Scheduled jobs cannot ask for clarification. Make a narrow, reversible recovery decision and verify with drift check plus remote containment.
