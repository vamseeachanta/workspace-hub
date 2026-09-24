---
name: crossprovider codex test-only-key-validation-should-default-fail-clo
description: Test-only key validation should default fail-closed, not trust artifact declarations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-posture, production-defaults, test-isolation]
---

Allowing tracked commitment artifacts to self-declare `test_only` and having production callers trust that flag creates fail-open conditions. Production code should default to rejecting test keys; tests explicitly override via environment variables, not artifact fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
