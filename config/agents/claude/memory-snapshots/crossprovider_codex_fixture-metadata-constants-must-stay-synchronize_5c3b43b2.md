---
name: crossprovider codex fixture-metadata-constants-must-stay-synchronize
description: Fixture metadata constants must stay synchronized with conversion logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-fixtures, metadata, synchronization]
---

Fixture metadata records conversion constants (e.g., oil_tonnes_to_bbl: 7.33) that are read by tests and shipped in output metadata. When conversion logic changes (e.g., density-driven factors replacing constants), fixture metadata must be updated or tests fail and real data gets wrong values. Treat fixture metadata as a contract that must be refreshed alongside implementation changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
