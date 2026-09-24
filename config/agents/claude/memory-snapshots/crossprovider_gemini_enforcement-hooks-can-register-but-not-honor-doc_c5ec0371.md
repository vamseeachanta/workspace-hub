---
name: crossprovider gemini enforcement-hooks-can-register-but-not-honor-doc
description: Enforcement hooks can register but not honor documented environment variables
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, enforcement, hooks, testing]
---

Hooks like `.claude/hooks/plan-approval-gate.sh` and `.git/hooks/pre-push` can be registered and installed but fail to read/respect documented environment variables (FORCE_PLAN_GATE_STRICT, DISABLE_ENFORCEMENT) that should control their behavior. Verification requires reading generated hook content and testing under different environment modes, not just checking docs or confirming hook registration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
