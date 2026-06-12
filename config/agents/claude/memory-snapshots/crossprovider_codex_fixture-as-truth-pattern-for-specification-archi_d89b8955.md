---
name: crossprovider codex fixture-as-truth-pattern-for-specification-archi
description: Fixture-as-truth pattern for specification architecture
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, specs, TDD]
---

When a spec has both YAML fixture and markdown rendering: fixture is authoritative for enforcement; markdown is reduced/human-readable view only. Consistency tests must verify all rendered columns are present in fixture; markdown rendering is non-normative. Fixture changes are the source of truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
