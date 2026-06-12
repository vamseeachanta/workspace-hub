---
name: crossprovider hermes git-sparse-overlay-reset-hard-wipes-overlay-file
description: Git sparse overlay: reset --hard wipes overlay files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, sparse-checkout, workspace, overlay]
---

`git reset --hard` on a sparse-checkout branch destroys overlay-layer files. Write to mount path (/mnt/local-analysis/) not overlay (~/) to persist changes across resets. Use direct file I/O or mount-aware tool invocations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
