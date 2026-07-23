> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_keep_data_at_fingertips.md

---
name: keep-data-at-fingertips
description: "Cleanup/dedup default: keep data close & backed up, delete only regenerable cruft — never delete data just because it's re-fetchable"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7fc54178-93fd-4fe5-8d10-8ccfc27a684f
---

When cleaning up disk / dedup'ing, the owner's principle (stated 2026-07-03) is: **"keep
as much data at fingertips as possible for the repo ecosystem; do NOT re-hunt for data
later."**

- **Delete only regenerable cruft** — build output, `__pycache__`/`.pyc`, `Thumbs.db`/
  `.DS_Store`, test/coverage caches, superseded snapshots (`*.bak`).
- **Do NOT delete data just because it's re-fetchable** (re-syncable cloud mirror,
  re-downloadable public dataset). "Re-fetchable" is not "disposable" — re-hunting later
  is the cost we're avoiding. If the cloud/source is itself being retired, the LOCAL copy
  becomes of-record and must be KEPT + backed up.
- **Critical data → maintain a backup** (≥2 copies, ≥1 offline). A single copy on a
  non-RAID disk is a single point of failure the moment the other copy (e.g., cloud) goes
  away.
- Backup/retention/data-exploitation work is **tracked via GH issues**, not done ad hoc.

**Why:** the value of data-at-fingertips (fast reuse, capability development) outweighs the
disk saved by deleting re-acquirable data. Reclaim space from cruft, not from the corpus.

**How to apply:** in a delete-review, tier each item as critical-keep / keep-at-fingertips
/ regenerable / disposable; only the last two are delete candidates. Concrete instance:
[[ace-share-cleanup-dedup]] — gdrive local mirror + osi-datasets were KEPT (not deleted),
and Epic wshub #3370 (+#3371–#3374) tracks inventory, backup policy, gdrive cloud-sunset,
and the prognostics/RUL capability spike.
