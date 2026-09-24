---
name: crossprovider codex output-status-contracts-must-be-internally-consi
description: Output status contracts must be internally consistent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contracts, output-design, consistency]
---

A record cannot simultaneously be 'in normalized output stream' and 'separate diagnostic'. Define clearly whether diagnostics (e.g., wiki-schema-warnings) flow through the same record pipeline or are separate. Internal contradictions block implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
