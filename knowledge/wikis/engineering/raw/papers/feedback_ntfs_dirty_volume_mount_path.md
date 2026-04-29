> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_ntfs_dirty_volume_mount_path.md

---
name: NTFS dirty-volume mount path
description: Use ntfs-3g (FUSE) for NTFS USB drives unplugged from Windows uncleanly; ntfs3 (in-kernel) refuses dirty volumes by default
type: feedback
originSessionId: 6d641720-6141-4aca-8a18-e75c30211e19
---
When mounting an NTFS volume on Linux that was hot-unplugged from Windows (no Eject), the in-kernel `ntfs3` driver fails with `volume is dirty and "force" flag is not set` and `mount` returns `wrong fs type, bad option, bad superblock`. Switch to `ntfs-3g` (FUSE userspace driver) — it auto-replays the NTFS journal and tolerates the dirty bit.

**Why:** Verified 2026-04-27 on ace-linux-1 with the WD Elements 4 TB portable. `ntfs3` errored out twice on the same volume; `ntfs-3g` succeeded immediately. `ntfs-3g` is intentionally permissive — it logs the dirty state but proceeds.

**How to apply:**

1. **Default to `ntfs-3g` for any NTFS USB drive that has been used on Windows.** Don't waste a round on `ntfs3` first; the failure mode looks like a kernel/option problem ("bad superblock") and misdirects diagnosis.
2. **Drop `default_permissions` and use `uid=$(id -u),gid=$(id -g),umask=022` for ownership.** A bare `ntfs-3g` mount yields `user_id=0,group_id=0,default_permissions` and files appear root-owned via FUSE's NTFS-ACL bridge — surprising on a personal drive. The explicit `uid`/`gid` make `stat()` return the user's IDs.
3. **Add `big_writes` for large copies.** FUSE default write granularity is 4 KB; `big_writes` raises it and meaningfully improves rsync throughput on large transfers. No downside.
4. **Don't run `ntfsfix` on a mounted volume.** It correctly refuses with "Refusing to operate on read-write mounted device". Only useful when the volume can't be mounted at all.
5. **The dirty bit doesn't auto-clear.** `ntfs-3g` replays the journal on every mount but doesn't write back a clean shutdown marker until the volume is properly unmounted. The authoritative fix is `chkdsk /f X:` from a Windows host — schedule it the next time the drive returns to Windows.
6. **For a known-clean read-only ingest** (e.g., the Elements drive ingest plan), mount with `-o ro,uid=$(id -u),gid=$(id -g),umask=022` — the `ro` flag is the durable safety, not the dirty-bit refusal.

**Do NOT apply when:** the volume is freshly Windows-formatted with a clean shutdown (`ntfs3` will mount fine and is faster), or the source is exFAT/FAT32 (different drivers entirely).
