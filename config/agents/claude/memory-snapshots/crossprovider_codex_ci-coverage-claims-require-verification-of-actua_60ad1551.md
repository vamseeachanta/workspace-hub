---
name: crossprovider codex ci-coverage-claims-require-verification-of-actua
description: CI coverage claims require verification of actual execution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [ci-coverage, testing-completeness, workflow-verification]
---

Listing both #68 and #63 scanners in the workflow does not prove both run. The #52 implementation claimed to cover #63 canary gates but actually only called the weaker #68 surface scanner. Tests must verify that all claimed scanners are actually invoked, not just that they exist in the codebase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
