---
name: crossprovider hermes auth-evidence-verification-gaps-leave-dispatch-f
description: Auth evidence verification gaps leave dispatch fail-open in readiness tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-design, auth-verification, readiness-dispatch]
---

Infrastructure readiness/dispatch tests check binary presence (CLI in PATH) but skip 'binary present, auth unavailable/expired' cases. This creates fail-open hole where host passes dispatch gate despite broken provider credentials. Acceptance criteria must require explicit auth-state evidence or safe `unknown => blocked` rule as first-class gate.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
