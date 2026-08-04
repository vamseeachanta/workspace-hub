---
name: reference_ecosystem_migrated_to_ext4_mnt_ace_ws
description: "2026-08-03: /mnt/local-analysis is now a SYMLINK to /mnt/ace/ws (ext4). git status went 11.6s → 23ms. Plus two migration traps: worktree repair repairs the wrong direction, and rsync buys one slow git status"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-03T16:33:21.936Z
---

## ⚠ `/mnt/ace/ws` IS THE CANONICAL WORKSPACE ROOT on ace-linux-1 (owner decision, 2026-08-03)

Use `/mnt/ace/ws/<repo>` for new work, briefs, dispatch prompts, and docs. `/mnt/local-analysis` is a **compatibility symlink** that keeps existing hooks, cron entries and configs working — it is legacy, not the address.

**`/mnt/local-analysis` is a symlink to `/mnt/ace/ws` (ext4) as of 2026-08-03.** All existing paths keep working. The NTFS-FUSE volume (`/dev/sdc1`, UUID `260E6F0E0E6ED679`) is detached but intact; fstab line 12 is commented; `/etc/fstab.bak-premigration` holds the original. Closes workspace-hub#3793.

**Measured, real repos, warm index:**

| repo | `git status` before | after |
|---|---:|---:|
| workspace-hub | 11,576 ms | **23 ms** (503×) |
| digitalmodel | 3,577 ms | **15 ms** (238×) |
| worldenergydata | — | **9 ms** |

`git describe --dirty`: workspace-hub 4,763 → 217 ms; digitalmodel 8,899 → 799 ms.

This retires the standing symptoms recorded elsewhere: `git status` timing out at >120 s, `git describe --dirty` at 38 s, and the contention collapse (a collect taking 7.56 s idle but 54.20 s under concurrent load — FUSE is a single userspace daemon, so parallel agents queue behind it).

## Trap 1 — `git worktree repair` repairs the WRONG DIRECTION after a whole-tree copy

`repair` resolves through a worktree's `.git` file to find "the" repository. After a copy that pointer still names the **source**. So running it from the destination rewrote the **source** repo's `gitdir` registrations to point at the new locations — damaging the rollback copy, not fixing the new one.

`repair` is designed for *"the worktree moved, the repo didn't."* When **both** move it has no anchor and follows the only pointer it has, backwards.

**Correct fix for a wholesale move** — rewrite both link files deterministically, touching only the destination:
```bash
# worktree side
find <newroot> -maxdepth 4 -name .git -type f -exec sed -i 's#<oldroot>/#<newroot>/#g' {} +
# repo side
find <newroot> -path '*/.git/worktrees/*/gitdir' -exec sed -i 's#<oldroot>/#<newroot>/#g' {} +
```
Then verify with `git worktree list` in **both** trees — each must resolve entirely within itself. 31 pairs needed rewriting here.

The tell was in `repair`'s own output: every line named the path being migrated *away from*.

## Trap 2 — every rsync into a git tree buys exactly one slow `git status`

Git's index caches `(dev, inode, ctime, mtime, size)` per file. `rsync -a` preserves mtime, but **inode and ctime are necessarily new** on the destination — so every file looks stat-dirty and the next `git status` re-hashes the entire worktree.

Measured: first run after sync **5,000–50,000 ms**; second run **9–23 ms**. The first run *rewrites* the index with correct stat data.

**Anyone benchmarking immediately after a sync measures the index rebuild, not the filesystem** — and would conclude the migration made things worse. This nearly happened twice; both times the second run was the truth. Always measure twice after any bulk copy into a git tree.

## Migration method that worked

1. Bulk `rsync -aHAX` (102 GB, 734,120 files, 4 h, 0 errors), excluding `.venv/`, `__pycache__/`, `node_modules/` (~27 GB, regenerable)
2. **Delta sync with writers quiesced** — mandatory: auto-sync kept committing to the source during the 4-hour bulk copy, so the trees had diverged. 368 files, 12 min.
3. Worktree link rewrite (both directions), re-run **after** the delta
4. `umount -l` (all holders were cwd-only, `..c..` in `fuser -vm`), comment fstab, `rmdir`, `ln -s`
5. Verify: HEADs match pre-migration, entry counts match, worktrees resolve, no residual old-path refs

**Operational note:** `sudo` password prompts consume subsequently-pasted lines as password input. Multi-line sudo blocks silently execute only the first command. Hand the user **one command at a time**.

## Open

- **Fleet divergence:** ace-linux-2 still mounts real NTFS at `/mnt/local-analysis` (fstab line 15 sshfs-mounts it here). Equality/readiness tooling will see the machines differ.
- `.venv/` excluded — repos need `uv sync` before suites run.
- `agent-worktrees` 27 GB (mostly merged branches) and `phone-media` 28 GB gain nothing from ext4 — 43% of what was migrated.

Related: [[reference_ntfs_fuse_git_stalls_local_analysis]] (superseded for the git-stall symptom), [[feedback_untracked_is_transient_commit_plans_immediately]], [[feedback_merge_is_not_done_until_branch_and_worktree_gone]].
