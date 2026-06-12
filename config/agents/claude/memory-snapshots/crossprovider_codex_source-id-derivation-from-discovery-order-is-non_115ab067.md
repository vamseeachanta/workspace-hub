---
name: crossprovider codex source-id-derivation-from-discovery-order-is-non
description: Source ID derivation from discovery order is non-deterministic
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [determinism, testing]
---

Source IDs like `source:0001` depend on filesystem/glob discovery order (#2767). Use stable IDs: sort source roots alphabetically before enumeration, or derive IDs from redacted source evidence IDs (hash). Add tests proving reordered roots produce identical classification references and IDs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
