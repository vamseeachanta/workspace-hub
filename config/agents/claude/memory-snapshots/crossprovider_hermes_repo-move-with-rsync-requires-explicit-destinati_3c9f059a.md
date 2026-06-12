---
name: crossprovider hermes repo-move-with-rsync-requires-explicit-destinati
description: Repo move with rsync requires explicit destination preservation and HEAD verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-move, rsync-safety, git-verification]
---

Moving repos via rsync to `/mnt/ace` with `--delete`: (1) preserve preexisting destination with timestamp-suffixed backup, (2) verify source HEAD matches destination HEAD post-sync, (3) remove source only after verification succeeds. Skip verification and you risk losing preexisting data or leaving stale sources in place.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
