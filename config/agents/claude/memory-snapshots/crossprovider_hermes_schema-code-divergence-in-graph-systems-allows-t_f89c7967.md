---
name: crossprovider hermes schema-code-divergence-in-graph-systems-allows-t
description: Schema-code divergence in graph systems allows tests to pass while violations exist
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, schema, test-coverage-gap]
---

llm-wiki #77 had schema docs explicitly excluding `docs/reports/**` from extraction, but the generator still emitted edges to those resources without scope filtering. Tests passed because they checked specific local patterns (forged nodes, unresolved-to-in-scope) but not the scope-boundary enforcement. Generator's `_resolve_repo_link()` lacks scope gating.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
