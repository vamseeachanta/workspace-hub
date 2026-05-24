# Session handoff — Hermes kanban ecosystem manifest (PUSH BLOCKED)

**Date:** 2026-05-23
**Session goal:** "prepare hermes kanban boards for each repo in the repo ecosystem folder"
**Status:** **Work complete locally; push to origin/main blocked.**

## What landed

### Committed locally on `main` (NOT yet on origin)

- `d6f4fcf79` — `feat(kanban): introduce Hermes kanban manifest for ecosystem (1 ecosystem + 14 repo + 30 domain boards, 1536 cards)`
- `908247944` — `chore(sync): auto-sync 2026-05-23 (pre-push runtime state)`
- Plus 7 other commits from parallel sessions (auto-sync, governance, session-handoff, etc.)

### Files added (`.claude/memory/kanban/`, 63 files, 1.2 MB)

```
SCHEMA.yaml           board YAML contract
README.md             governance + cross-machine sync model
manifest.yaml         top-level index (45 boards, 1536 cards, 75 gaps)
boards/               45 board YAMLs (1 ecosystem + 14 repo + 30 domain)
gaps/                 14 gap files (75 detected-gap cards awaiting GH-issue promotion)
scripts/load.py       idempotent loader (--initial-status blocked + idempotency-key)
```

### Live in Hermes runtime (`~/.hermes/kanban.db`)

- **45 boards** provisioned via `hermes kanban boards create`
- **1536+ cards** loaded via `hermes kanban create --initial-status blocked --idempotency-key gh:<owner>/<repo>#<num>`
- **~530 extra auto-decomposed children** spawned by gateway specifier+decomposer from the first (pre-patch) batch of 134 triage cards
- See per-board breakdown in the final summary further down

## Repo ecosystem coverage

| Tier | Count | Notes |
|---|---|---|
| 0 ecosystem | 1 board, 20 cross-repo themes | Synthesized from MEMORY.md |
| 1 repo | 14 boards | One per active repo (7 with overflow cards, 7 empty parents) |
| 2 domain | 30 boards | workspace-hub × 6, digitalmodel × 5, achantas-data × 5, worldenergydata × 4, llm-wiki × 4, assethold × 3, sabithaandkrishnaestates × 3 |
| **Total** | **45 boards** | All in Hermes; 1536 mirrored cards (1516 GH issues + 20 themes) |

Skipped repos (dormant or foreign-owner): `achantas-media`, `teamresumes`, `worldenergydata-wiki`, `CAD-DEVELOPMENTS` (owned by `bakkiprasad5669/`).

## Why push is blocked

1. **Origin/main is 5 commits ahead of local** — must integrate before push.
2. **`Claude Code statusline-command.sh` runs `git status` every few seconds** → constant `.git/index.lock` contention → my `git add -u` / `git commit` race-fail with "Another git process seems to be running".
3. **Concurrent auto-sync daemons modify 44+ tracked files continuously** → working tree never settles; `git pull --rebase --autostash` keeps failing with `fatal: Cannot autostash`.
4. **JSONL merge conflict on `.claude/state/session-signals/2026-05-22.jsonl`** — both local and remote auto-sync commits append to it; standard `git rebase` cannot auto-resolve.
5. **Orphan `git stash pop` from earlier `--autostash` attempt held lock for 1:41** (was killed).
6. **First worktree materialization completed in 17 min; second attempt stalled past 1h+** — likely I/O contention with 260+ leftover Hermes workers + parallel agent sessions on this machine.

## Recommended next-session action

**Push as a feature branch instead of to main:**

```bash
cd /mnt/local-analysis/workspace-hub
GIT_OPTIONAL_LOCKS=0 git push origin d6f4fcf79:refs/heads/kanban-manifest-2026-05-23
```

This bypasses every blocker above — no rebase, no clean WT requirement, no conflict, no worktree materialization. Then open a PR via `gh pr create` and merge via GitHub UI, which handles JSONL union-merge server-side.

Optionally also push `908247944` if desired (the auto-sync commit for runtime state).

## How to resume the live load if needed

Loader is idempotent. To re-sync any machine:

```bash
cd /mnt/local-analysis/workspace-hub
git pull
python3 .claude/memory/kanban/scripts/load.py --dry-run    # preview
python3 .claude/memory/kanban/scripts/load.py              # actual
```

Re-runs are safe: `--idempotency-key gh:<owner>/<repo>#<num>` returns existing task IDs instead of creating duplicates.

## Key gotchas discovered this session (saved to memory)

- **Hermes `--initial-status blocked` is NOT a park spot** — the gateway specifier auto-unblocks blocked-without-reason cards to `ready` within minutes. The pre-existing `default`-board blocked tasks survive because they have `blocked_reason` / `consecutive_failures` set. See `feedback_hermes_blocked_status_auto_unblocked.md`.
- **Hermes `--triage` is the ENTRY of the auto-pipeline, not a park spot.** Specifier promotes triage→todo; decomposer fans out from there. 134 triage cards spawned 532 auto-decomposed children + 260 active worker processes. See `feedback_hermes_triage_is_pipeline_entry.md`.
- **Workspace-hub worktree materialization is indeterminate-duration** under parallel-agent load: 17 min one attempt, 1h+ stalled another. See `feedback_worktree_materialization_variance.md`.
- **`git rebase --autostash` fails ("Cannot autostash") when statusline lock-races with the stash creation.** Direct `git stash push -u -m` may also fail silently. The lock-storm window is too tight for autostash to survive on this repo. See `feedback_autostash_lock_race_workspace_hub.md`.

## Files / artifacts

- Manifest: `.claude/memory/kanban/manifest.yaml`
- Schema: `.claude/memory/kanban/SCHEMA.yaml`
- Loader: `.claude/memory/kanban/scripts/load.py`
- Governance: `.claude/memory/kanban/README.md`
- 45 board YAMLs: `.claude/memory/kanban/boards/`
- 14 gap files: `.claude/memory/kanban/gaps/`
