---
name: crossprovider codex metadata-claims-require-cross-check-against-actu
description: Metadata claims require cross-check against actual payload, not structure alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, data-provenance, metadata-truthfulness]
---

Coverage status "complete" must be verified by iterating actual payload fields and checking factors exist for each, not by inspecting sidecar structure only. Stale or hand-edited sidecars can claim completeness while missing fields or containing unrelated accepted factors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
