---
name: crossprovider codex deterministic-ordering-requires-complete-and-exp
description: Deterministic ordering requires complete and explicit join keys
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [database-design, determinism, identity-keys]
---

If rows are identified by (response_id, dof, frequency, heading) but envelope_sha256 is omitted from the key, two approved envelope revisions sharing one response_id collide and sorting becomes non-deterministic. Join-key definitions must be explicitly closed; implicit deduplication leads to under-specified composition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
