---
name: crossprovider codex test-only-issues-need-explicit-staging-rules
description: Test-only issues need explicit staging rules
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, staging, sequencing, ci-gates]
---

Test-focused plans that cannot be merged to main before prerequisites land must define concrete staging: separate test branch with explicit lift-off criteria, xfail-with-unblock mechanism, or manual gate with clear unlock condition. "Don't merge yet" alone leaves implementers without a deployment path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
