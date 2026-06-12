---
name: crossprovider hermes root-workspace-fuse-hidden-cleanup-in-micro-clos
description: Root workspace fuse_hidden cleanup in micro-closeout
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [root-cleanup, fuse-hidden-files, workspace-hub]
---

Root accumulates hook/session-generated untracked files (.planning/quick/.fuse_hidden*). Include explicit cleanup/stat check in final root micro-closeout; these are disposable and should not block clean proof.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
