---
name: crossprovider codex cross-repository-releases-require-immutable-exac
description: Cross-repository releases require immutable exact-SHA pinning and readback verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [release, immutability, cross-repo-contract]
---

Floating dataset revisions, off-origin redirects, and LFS shards are not immutable evidence. Use bounded regular Git blobs with exact-SHA resolve paths only. Publisher must capture and verify returned SHA via readback to confirm the published artifact matches intent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
