---
name: crossprovider codex docs-and-evals-can-claim-behavior-that-validator
description: Docs and evals can claim behavior that validators actually reject
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [spec-impl-gap, test-coverage, coherence]
---

Common pattern: documentation and test fixtures permit a state or route (e.g., 'provisional review' status, merged-range report classification), but the actual validator code has no execution path for it, forcing fallback to `excluded_no_ingest` or rejection. Creates spec-implementation mismatch. Audit docs/evals against validator execution paths, not just test fixture shapes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
