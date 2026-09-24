---
name: crossprovider codex content-value-gate-on-extractable-text-not-encry
description: Content-value gate on extractable text, not encrypted flag alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [content-filtering, pdf-extraction, correctness]
---

A PDF that is encrypted but extractable (words_per_page >= 10, total_words >= 200) should proceed to full extraction, not be skipped. Gate on actual content quality, not the encrypted status. This fixes the bug where readable-but-encrypted standards were downgraded to metadata stubs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
