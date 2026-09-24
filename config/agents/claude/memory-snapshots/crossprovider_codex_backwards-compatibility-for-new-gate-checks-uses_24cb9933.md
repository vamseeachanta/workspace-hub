---
name: crossprovider codex backwards-compatibility-for-new-gate-checks-uses
description: Backwards compatibility for new gate checks uses WARN not FAIL
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, backwards-compatibility, governance, implementation-pattern]
---

When adding new gate checks (e.g., claim_gate), items created before the WRK must emit WARN, not hard failure, for missing metadata fields. Only items created after the WRK require the new fields to pass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
