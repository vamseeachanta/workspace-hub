---
name: crossprovider hermes readiness-checks-must-fail-closed-on-missing-con
description: Readiness checks must fail-closed on missing configuration
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, dispatch, fail-closed, security]
---

Dispatch readiness should validate env vars, permissions, workspace state, and remote evidence; missing ANY element blocks dispatch (fail-closed). Do not default to permissive/best-effort behavior; explicit verification required for safety-critical paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
