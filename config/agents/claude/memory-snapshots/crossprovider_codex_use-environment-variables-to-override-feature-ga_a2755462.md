---
name: crossprovider codex use-environment-variables-to-override-feature-ga
description: Use environment variables to override feature gates during testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-pattern, feature-gates, test-isolation]
---

Feature gates controlling branch execution (e.g., content availability checks) can be overridden via environment variables (e.g., `CONTENT_SUB_GATE_PASS=false`) to test alternative code paths without external dependencies. Enables isolated testing of Branch B logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
