---
name: crossprovider codex hard-link-publication-atomicity-pattern
description: Hard-link publication atomicity pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [atomicity, publication, hard-links, resource-management]
---

Exclusive backing creation + descriptor-relative hard link + fsync parent achieves atomic publication resistant to concurrent overwrites. Validate hard-link count and inode before and after publication. No-replace semantics with preserved residue on failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
