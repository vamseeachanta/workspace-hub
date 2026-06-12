---
name: crossprovider hermes enforcement-environment-not-sourced-in-pre-push-
description: Enforcement environment not sourced in pre-push hook
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [enforcement, hooks, pre-push, governance-gap]
---

.git/hooks/pre-push does not source scripts/enforcement/enforcement-env.sh, even though SESSION-GOVERNANCE.md documents DISABLE_ENFORCEMENT and FORCE_PLAN_GATE_STRICT as central controls. The plan-approval-gate.sh hook hardcodes enforcement logic and never reads FORCE_PLAN_GATE_STRICT; it only respects SKIP_PLAN_APPROVAL_GATE. This design mismatch blocks local enforcement overrides at push time (#2127, #2128).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
