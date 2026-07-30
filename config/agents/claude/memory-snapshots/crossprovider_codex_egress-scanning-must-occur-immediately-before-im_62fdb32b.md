---
name: crossprovider codex egress-scanning-must-occur-immediately-before-im
description: Egress scanning must occur immediately before immutability, not before mutation phases
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [egress-validation, mutation-ordering, defense-in-depth]
---

Gates that scan reports before upload miss mutations that occur at the upload boundary. If a report is scanned, then pinned/mutated, then uploaded, the final emitted bytes are unscanned. Move egress validation to occur after all document mutations and immediately before the operation that makes output immutable or public.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
