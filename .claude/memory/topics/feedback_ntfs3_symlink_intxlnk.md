> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_ntfs3_symlink_intxlnk.md

---
name: ntfs3 breaks IntxLNK symlinks
description: In-kernel ntfs3 driver does not resolve NTFS symlinks (IntxLNK reparse points); they appear as regular files with raw payload — breaks git, hooks, plugin links
type: feedback
originSessionId: cc620d91-a0f1-4867-a63f-617d1dfb5d0f
---
The in-kernel `ntfs3` driver (Linux 6.x) **does not resolve NTFS symlinks created by `ntfs-3g`**. After swapping a mount from `ntfs-3g` (FUSE) to `ntfs3` (in-kernel), every symlink on the volume becomes visible as a small regular file whose first bytes are the magic header `IntxLNK` followed by the target path. `readlink()` fails, `ls -la` shows no `->` arrow, executing the file invokes bash with `IntxLNK<target>` as a literal command.

**Why:** Verified 2026-05-01 on ace-linux-1, `/dev/sdc1` (workspace-hub volume, NTFS). After `ntfs3-trial.sh swap`, the workspace-hub `commit-msg` hook (a symlink to `../../.claude/hooks/check-commit-msg.sh`) became an 86-byte regular file containing `IntxLNK../../.claude/hooks/check-commit-msg.sh`. Bash tried to execute `IntxLNK...` as a command and failed. `git status` showed `T` (type-change) for every git-tracked symlink in the repo (`.claude/skills/skills`, `.codex/skills`, `.gemini/skills`, `scripts/ecosystem_sync`, `scripts/setup/fea-pkgs/...changelog.Debian.gz`).

**How to apply:**

1. **Default to `ntfs-3g` for any NTFS volume that hosts a git repo, plugin tree, or anything with symlinks.** This rules out ntfs3 for the workspace-hub volume specifically.
2. **NEVER commit while ntfs3 is mounted.** Type-changed symlinks would land in git as raw `IntxLNK` blobs and corrupt history. If you discover the swap mid-session with staged or modified files, do NOT `git add -A` or commit — rollback first.
3. **If a swap was attempted and rolled back**, verify symlinks are restored before any git operation: `ls -la <known-symlink>` should show `->` arrow; `git status` should not show `T` entries for previously-tracked symlinks.
4. **The 77x git_log regression observed in the perf-bench trial is likely caused by this same issue** — git's pack/ref/object directories use symlinks heavily and ntfs3's failure to resolve them forces fallback paths.
5. **Linux 6.17 still has this limitation.** Kernel ntfs3 partially supports NTFS symlinks under specific conditions (volume created on Linux with ntfs3 from scratch), but symlinks created by ntfs-3g are not interoperable. Don't expect a kernel update to silently fix this — re-test before swapping again.

**Do NOT apply when:** the volume has zero symlinks (e.g., a Windows-created ingest drive carrying only documents/binaries) — ntfs3 is then a fine, faster choice. Probe first: `find /mnt/path -type l 2>/dev/null | head -5`.

**Related:** `feedback_ntfs_dirty_volume_mount_path.md` — covers the dirty-bit refusal failure mode for ntfs3 (separate concern).
