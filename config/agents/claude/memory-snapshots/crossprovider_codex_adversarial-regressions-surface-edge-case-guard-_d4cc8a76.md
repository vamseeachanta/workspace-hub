---
name: crossprovider codex adversarial-regressions-surface-edge-case-guard-
description: Adversarial regressions surface edge-case guard bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [testing, edge-cases, governance]
---

Normal test suites won't detect dead scopes, sentinel bypasses, or nested abort violations. Design regressions specifically to VIOLATE the intended guard to find these edge cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
