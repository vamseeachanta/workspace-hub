---
name: crossprovider codex checksum-verification-must-normalize-paths-after
description: Checksum verification must normalize paths after structural migration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, verification, checksum]
---

When verifying file integrity across a migration that changes directory structure, compute checksums on both source and target, then normalize the paths in the checksum outputs before diffing. Direct checksum comparison fails because paths have changed, not content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
