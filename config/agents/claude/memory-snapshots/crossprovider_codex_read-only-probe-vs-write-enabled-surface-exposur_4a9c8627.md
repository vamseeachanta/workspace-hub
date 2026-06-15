---
name: crossprovider codex read-only-probe-vs-write-enabled-surface-exposur
description: Read-only probe vs write-enabled surface exposure
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [surface-design, authorization, data-governance]
---

Before exposing a domain dataset (especially vendor/private data) to an orchestration layer, distinguish 'can query' from 'should drive autonomous actions'. Requires boundary review: licenses, schemas, private-data redaction, scope authorization. Expose as read-only probe, not write input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
