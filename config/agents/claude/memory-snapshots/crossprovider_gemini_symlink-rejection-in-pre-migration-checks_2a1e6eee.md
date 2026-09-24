---
name: crossprovider gemini symlink-rejection-in-pre-migration-checks
description: Symlink rejection in pre-migration checks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration-safety, preflight-checks, symlink-handling]
---

Disallow symlinks in migration scope during preflight validation. Symlinks in source break assumptions about file copying and pointer replacement, introducing silent failure modes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
