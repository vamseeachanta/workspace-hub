---
name: crossprovider codex revalidate-private-input-boundaries-at-every-rea
description: Revalidate private-input boundaries at every read, not just creation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [privacy-boundaries, multi-pass-validation, mutation-safety]
---

Snapshot creation validates directory privacy/permissions, but snapshot reads that don't revalidate allow same-digest copies in tracked/permissive locations to pass. Before every snapshot open—especially around replacement/mutation—recheck private location, no symlink components, regular file, and owner-only mode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
