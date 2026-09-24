---
name: crossprovider codex test-coverage-gaps-hide-behavior-mode-mismatches
description: Test coverage gaps hide behavior mode mismatches in enforcement hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, governance, code-quality]
---

Enforcement/governance features support multiple modes (strict, advisory, disabled) but tests cover only the primary path. Gaps in advisory/disabled mode coverage let documented behavior diverge from actual implementation. Sibling code (e.g., require-review-on-push.sh honoring FORCE_PLAN_GATE_STRICT) provides reference patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
