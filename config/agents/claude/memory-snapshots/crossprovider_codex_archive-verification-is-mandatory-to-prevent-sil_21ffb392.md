---
name: crossprovider codex archive-verification-is-mandatory-to-prevent-sil
description: Archive verification is mandatory to prevent silent data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [cleanup, archive, verification]
---

After removing stale files, verify cleanup tarballs are readable via `tar -tzf`. Silent archive corruption is invisible in clean-state reports and allows undetectable data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
