---
name: crossprovider gemini enforcement-environment-variables-don-t-propagat
description: Enforcement environment variables don't propagate through all gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [governance, enforcement, gates, environment-variables]
---

FORCE_PLAN_GATE_STRICT and DISABLE_ENFORCEMENT are documented governance controls in enforcement-env.sh but don't propagate through all enforcement surfaces (plan-approval-gate.sh, pre-push chains). Enforcement code often hardcodes defaults or uses undocumented bypass vars (SKIP_PLAN_APPROVAL_GATE), causing documented controls to be inert at runtime.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
