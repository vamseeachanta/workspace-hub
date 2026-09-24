---
name: crossprovider codex hermetic-test-fixture-contract-binds-isolation-b
description: Hermetic test fixture contract binds isolation boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, hermetic-builds, cross-platform]
---

Safe cross-platform fixtures require: pre/post-step command stubs, HOME isolation, controlled PATH, Windows continuation semantics, allowlisted invocation ledger, and fail-closed guard on unexpected host access. Missing any boundary allows test/prod divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
