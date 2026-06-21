---
name: crossprovider codex privacy-scanning-use-positive-pattern-exclusion-
description: Privacy scanning: use positive-pattern exclusion, not just expected-field confirmation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [security, privacy, artifact-generation]
---

When generating artifacts from sensitive source data, scan with positive patterns of what must NOT appear: raw `/mnt/`, `/home/`, `/tmp/` paths; source filenames; excerpts; email patterns; credential-shaped strings (token=, password=, etc.). This catches leakage through unexpected fields, not just confirms safe fields exist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
