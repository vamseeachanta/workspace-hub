# Session handoff — `D:\ws` repo ecosystem cleanup (ace-win-1 Windows box)

**Date:** 2026-07-06 (work performed 2026-06-28 → 06-30)
**Box:** ace-win-1 equality column (Windows, checkout root `D:\ws`)
**Scope:** full hygiene pass across every git repo under `D:\ws` — goal: no dirty work, no lost work, no stale branches/worktrees/stashes, no stale files/artifacts.

## Outcome — all repos clean

| Repo | Working tree | Sync | Stashes | Branches | Notes |
|---|---|---|---|---|---|
| llm-wiki | clean | ✓ | 0 | main | wiped index restored (49,080 files); 73 long-path files recovered |
| llm-wiki-acma | clean | ✓ | 0 | main | was already clean |
| assetutilities | clean | ✓ | 0 | main | cleanup merged (PR #108) |
| worldenergydata | clean | ✓ | 0 | main | cleanup merged (PR #671) |
| digitalmodel | clean | ✓ | 0 | main | cleanup merged (PR #1160) |
| workspace-hub | clean | ✓ | 0 | main | nested repos locally excluded |
| doris (nested) | clean | ✓ | 0 | main | synced clone; kept (see open items) |

**Removed clones:** `seanation` and `acma-projects` (both nested under workspace-hub) — fully backed up first (see below).

## Root causes fixed
- **Wiped git index** in llm-wiki (0 tracked vs 49,080 in HEAD) — restored via `read-tree`/checkout.
- **Windows 260-char path limit** — set `git config --global core.longpaths true`.
- **No symlink-creation privilege on this box** — set `git config --global core.symlinks false` so tracked symlinks materialize as text files (match blobs → clean). Setting `core.symlinks=true` here BREAKS every repo (typechanges, blocked rebases).
- **~1,000,000 transient scratch files** (`.codex/Cu*/`, `.gemini/Cu*/`) across 4 repos — gitignored (canonical block) and deleted from disk.
- **Merge-conflict junk symlinks** (`*~Updated upstream`) removed from assetutilities.
- **Dubious-ownership** (checkouts owned by `ansystech`, session runs as another user) — `safe.directory` added per repo.

## Stashes & stale branches (no-loss policy)
- **Stashes:** 23 → 0. One provably-redundant test-report stash dropped; the rest preserved as `stash-backup/*` tags, then (2026-06-30) bundled to durable backups and the tags deleted.
- **Stale branches:** backed up to their origins then deleted locally (`docs/openai-prompting-guide`, `master`, `feat/implement-ss-naming-in-code`, `chore/wrk-470-windows-merge-fix`, `merge-main`). `worldenergydata/202502` could not be pushed (repo over Git LFS budget) — bundled locally (incl. its LFS blobs) then deleted.

## Backups (safety net — outside the workspace)
`D:\backups\ws-cleanup-2026-06-30\` — **~12.3 GB total**, every deletion verified against a bundle first (`git bundle verify`) before removal:
- `acma-projects-full.bundle` (~1.97 GB) — full `--all`, includes the 2 unpushed commits (HEAD `d06c20b0`: P19XX brief + AI-session gitignore).
- `worldenergydata-202502.bundle` (~1.55 GB) + `worldenergydata-git-lfs\` (~4.92 GB LFS blobs).
- `digitalmodel-stash-backup-0.bundle` (~2.4 GB) — preserves unique `sync_all_clean.py`.
- `worldenergydata-stash-backup-0.bundle` (~1.33 GB), `workspace-hub-stash-backups.bundle` (~118 MB, all 10 tags).

Restore any item with `git clone`/`git fetch <bundle>`.

## External actions taken (for transparency)
- Pushed cleanup commits + merged 3 PRs (#108/#671/#1160) — each on explicit user instruction ("merge PRs"); API auth via the token already in Windows Credential Manager (no new auth). worldenergydata #671 waited for its 11 required CI checks to go green.
- Pushed stale branches to their existing origins as backups before local deletion.
- No pushes to acma-projects (archived — left unpushed per user); no writes to any private client repo beyond the above.

## Open items for the user
1. **`doris`** nested clone — fully synced to GitHub, kept. Remove like seanation/acma-projects if desired.
2. **`worldenergydata/202502`** — its LFS-budget push blocker is now moot (bundled locally); increase the LFS budget only if you want it back on the remote.
3. **Backups (`D:\backups\ws-cleanup-2026-06-30`, ~12.3 GB)** — retained as insurance; delete once satisfied nothing is needed.
4. **acma-projects** is archived; route future client/project content to `llm-wiki-acma` (per user 2026-06-29).

## Memory updated (this box's auto-memory)
- `reference-ws-git-windows-settings` — required global git settings (longpaths, symlinks-as-text) + scratch-ignore + safe.directory.
- `project-acma-projects-archived-route-to-llm-wiki-acma` — archived; clone removed + bundle location.
- (this box's equality-identity memory) — equality-column identity + sanitize-host-before-push practice.
