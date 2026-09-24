---
name: crossprovider codex preflight-symlink-rejection-in-migrations-preven
description: Preflight symlink rejection in migrations prevents logical-path divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, filesystem-safety]
---

Before executing file migrations, check for and explicitly reject symlinks under the migration scope. Symlinks create two valid logical paths to the same content, causing hard-to-debug state divergence when migration scripts assume one-to-one path mapping.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
