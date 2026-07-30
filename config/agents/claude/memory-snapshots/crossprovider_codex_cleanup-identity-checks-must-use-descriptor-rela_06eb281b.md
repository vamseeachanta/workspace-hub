---
name: crossprovider codex cleanup-identity-checks-must-use-descriptor-rela
description: Cleanup identity checks must use descriptor-relative ops to avoid TOCTOU
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [toctou, cleanup-safety, atomic-binding]
---

Stat-then-unlink cleanup has a TOCTOU window where a replacement file at the same path can be deleted despite different identity. Validation (stat) and deletion (unlink via pathname) are separate syscalls; a substitution between them bypasses the identity check. Use descriptor-relative ops (fstat + fchmod + fstat + unlink via fd) or hold the identity-bound fd until deletion completes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
