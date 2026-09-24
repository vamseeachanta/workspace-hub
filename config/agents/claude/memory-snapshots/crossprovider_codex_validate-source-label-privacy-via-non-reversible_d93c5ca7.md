---
name: crossprovider codex validate-source-label-privacy-via-non-reversible
description: Validate source-label privacy via non-reversible commitments, not exact-label maps in code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, code-pattern, validation, source-handling]
---

When generated content must hide exact sensitive identifiers (e.g., exact source labels), store a SHA-256 commitment of the identifier plus its opaque handle in configuration, then validate at runtime by comparing commitments only—never by storing or comparing the exact value. Config should use `source_label=None` with a separately computed commitment; exception paths should reference only the code ID/rank, not the untrusted label value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
