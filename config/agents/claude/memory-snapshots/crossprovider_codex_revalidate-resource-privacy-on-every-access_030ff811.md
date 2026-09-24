---
name: crossprovider codex revalidate-resource-privacy-on-every-access
description: Revalidate resource privacy on every access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, file-handling, privacy]
---

Resource privacy constraints (file permissions, location residency, symlink-free structure) should be revalidated on every access attempt, not just at creation time. Same-digest copies in non-private locations can evade creation-time validation if privacy is not checked before each use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
