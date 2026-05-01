---
name: Elements external drive identity
description: WD Elements 4 TB external drive — UUID, mount conventions, dirty-bit state, links to ingest handoff
type: project
originSessionId: 6d641720-6141-4aca-8a18-e75c30211e19
---
The "Elements" drive referenced across ace-drive ingest planning is a WD Elements Portable 4 TB USB drive (model `WDC_WD40NDZW-11BYXS0`). When attached to ace-linux-1, it enumerates as `/dev/sdi1`. Stable identifiers (preferred over `/dev/sdX`):

- **NTFS volume UUID:** `94183792183771FA` (use this in `/etc/fstab` and mount commands)
- **USB id:** `usb-WD_Elements_2621_575841324435344136375A5A`
- **Inner ATA id:** `ata-WDC_WD40NDZW-11BYXS0_WD-WXA2D54A67ZZ`
- **Filesystem:** NTFS, label `Elements`
- **Capacity:** 3.7 TB total, 1.8 TB used, 1.9 TB free (~49% as of 2026-04-27)
- **Canonical mountpoint on ace-linux-1:** `/mnt/elements`

**Why this is in memory and not just inferable:** the device node (`/dev/sdi`) is dynamic and the drive isn't always plugged in, so future sessions can't discover identity from `lsblk` alone. The UUID is the only stable handle for fstab and scripts.

**How to apply:**

1. **Always mount by UUID, not `/dev/sdX`** — `sdi` can become `sdj` or another letter on replug.
2. **The drive is in the middle of a planned ingest into `/mnt/ace/` per `docs/sessions/2026-04-27-elements-drive-ingest-handoff.md`.** Cross-references: workspace-hub#1355, #1540, #1544, #1757, #1904. Do not start rsync work without reading that handoff and getting `status:plan-approved` on the ingest issue.
3. **The volume's NTFS dirty bit is set** — last clean shutdown was on Windows before an unclean unplug. `ntfs-3g` replays journal on every mount; pending Windows-side `chkdsk /f` is overdue but not blocking.
4. **Default mount mode is read-only.** The handoff doc locks "Source mounted read-only … Never write back to Elements" as the safety strategy. Use `-t ntfs-3g -o ro,uid=$(id -u),gid=$(id -g),umask=022 UUID=94183792183771FA /mnt/elements`. RW mounts are a policy deviation and should be flagged in any session note.
5. **No `/etc/fstab` entry exists** as of 2026-04-27 — auto-mount is intentionally deferred until the ingest plan completes and the RO policy is durably encoded.

**Update conditions:** when the ingest completes and the drive is retired, mark this memory archived. When `chkdsk` is run from Windows and the dirty bit clears, update the dirty-bit note.
