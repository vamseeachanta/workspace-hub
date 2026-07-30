---
name: crossprovider codex serialization-format-changes-corrupt-data-silent
description: Serialization format changes corrupt data silently through round-trip parsers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [serialization, data-integrity, testing]
---

Decimal('100') → '1' when trailing zeroes are stripped; ranking re-parses the corrupted string, changing winner. Tests only exercised one format ('60.0'). Round-trip serialization must be idempotent; tests must verify format preservation across all value classes, not just sample cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
