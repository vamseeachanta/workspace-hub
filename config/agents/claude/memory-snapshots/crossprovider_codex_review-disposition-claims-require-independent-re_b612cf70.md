---
name: crossprovider codex review-disposition-claims-require-independent-re
description: Review disposition claims require independent re-verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, verification, false-negatives]
---

When an r2 verdict claims a prior finding is 'resolved,' re-test the actual HEAD. Found case where r2 said 'status CSV issue fixed' but HEAD still silently drops data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
