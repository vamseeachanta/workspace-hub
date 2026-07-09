---
name: crossprovider codex fixture-isolation-for-boundary-semantics
description: Fixture isolation for boundary semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, fixtures, fail-closed, boundaries]
---

When a single fixture serves both fail-closed and operational authorization paths, create separate fixture files. Mutating a shared fixture to test both paths risks making both paths permissive; isolation reveals and enforces boundary differences.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
