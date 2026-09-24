---
name: crossprovider codex health-checks-must-fail-closed-on-missing-or-sta
description: Health checks must fail-closed on missing or stale data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [observability, status-semantics, testing]
---

Health scripts that skip accounting for missing manifests or data without timestamps can report false-GREEN states. Missing data must be counted as failures (increment failure counters), not skipped. Require tests proving missing data blocks health clearance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
