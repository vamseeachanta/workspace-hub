---
name: crossprovider codex malformed-data-perpetuates-on-publication
description: Malformed data perpetuates on publication
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [data, publishing, validation]
---

Misaligned CSV fields (header column count ≠ row field counts) will propagate if published without validation. Always validate field alignment and row structure before external export.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
