---
name: crossprovider codex transactional-staging-required-for-multi-step-fi
description: Transactional staging required for multi-step file operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-operations, transactionality, reliability]
---

Converting files directly to their destination without atomic promotion or stale-cleanup enables retry bugs and false attestation of stale output. Use staging directories (temp/isolated paths), validate fully, then promote on success or explicitly reject/clean failed output. Validate existence and reject partial/stale state before retry.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
