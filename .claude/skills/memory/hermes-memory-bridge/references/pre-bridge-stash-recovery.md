# Pre-bridge stash recovery when unrelated untracked files block commit

Use when `scripts/memory/pre-bridge-quality.sh --fix` generates memory bridge changes, but exits nonzero during its internal commit step after stashing the generated bridge output. The common failure text is either `nothing added to commit but untracked files present` or `nothing to commit, working tree clean` immediately after a `pre-bridge-stash` was created.

## Observed shape

- `check-memory-drift.sh` exits `1` with drift.
- `pre-bridge-quality.sh --fix` reports a passing quality score and runs `bridge-hermes-claude.sh`.
- Bridge updates `.claude/memory/agents.md`, `.claude/memory/context.md`, `.claude/memory/claude-auto-memory.md`, and `.claude/memory/topics/`.
- Bridge stashes before pull, then commit finds no staged changes because the generated bridge output is inside the stash (`nothing to commit, working tree clean`) or because unrelated untracked files remain (`nothing added to commit but untracked files present`).
- The memory changes are preserved in the newest stash, usually named `pre-bridge-stash`.

## Recovery pattern

From the workspace-hub repo root:

```bash
git stash list --date=local | head -5
git stash show --name-only stash@{0} | sed -n '1,160p'
```

Verify the newest stash contains only/primarily `.claude/memory/` bridge outputs you intend to recover. Then restore only memory paths:

```bash
git checkout stash@{0} -- .claude/memory
git status --short .claude/memory
git add .claude/memory
git commit -m "chore(memory): bridge Hermes memory"
git push
```

`git add .claude/memory` is required after restoring from the stash; do not assume restored paths are staged. If the push reports `Everything up-to-date`, do not treat that as failure by itself — local hooks or automation may already have pushed the commit. Verify `HEAD` equals `origin/main` / `@{u}` before reporting push success.

After push, verify sync and upstream parity:

```bash
bash scripts/memory/check-memory-drift.sh
git rev-parse HEAD
git rev-parse @{u}
git push --dry-run
```

If `HEAD` equals `@{u}`, drift check is clean, and dry-run says `Everything up-to-date`, the bridge is complete.

Drop the redundant generated stash only after verifying the memory commit is pushed **and** the stash contains no non-memory tracked changes you still need to preserve:

```bash
git stash show --name-only stash@{0}
# If output is limited to .claude/memory/ paths you recovered and pushed:
git stash drop stash@{0}
```

If the stash includes non-memory paths outside the bridge scope (for example logs, skill-patch ledgers, or other tracked files), do **not** drop it during a memory-bridge cron run. Report that the stash was preserved and name why. The bridge task's authority is to commit `.claude/memory/` only, not to discard unrelated work captured by the bridge's pre-pull stash.

## Hook-block recovery: forensic conflict markers in memory topics

Sometimes mirrored Claude topic files intentionally document literal merge-conflict markers inside fenced code blocks. The workspace pre-commit hook can still block these as unresolved conflict markers, e.g. in `.claude/memory/topics/feedback_origin_committed_with_unresolved_markers.md`.

Recovery:

1. Inspect the reported file and confirm the marker lines are forensic/example text, not an actual unresolved Git conflict.
2. Add the per-line exemption suffix to only the literal marker lines:

```text
<<<<<<< HEAD # CONFLICT_MARKER_FORENSIC_OK
======= # CONFLICT_MARKER_FORENSIC_OK
>>>>>>> Stashed changes # CONFLICT_MARKER_FORENSIC_OK
```

3. Re-stage `.claude/memory/` and retry the commit.

Do **not** bypass hooks with `--no-verify` for routine memory bridge commits. Do **not** blanket-rewrite or drop the topic file; preserve the memory content and annotate only the forensic marker lines.

## Guardrails

- Do **not** add unrelated untracked files just to satisfy the bridge commit.
- Do **not** pop/apply the whole stash into a dirty repo; restore only `.claude/memory/` paths.
- Report unrelated untracked files as pre-existing if they remain outside `.claude/memory/`.
- Final report should include quality score, drift count, updated memory file line counts, commit SHA, push status, and post-run drift status.
