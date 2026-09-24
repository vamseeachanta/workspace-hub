---
name: crossprovider gemini bypass-event-logging-exists-asymmetrically-acros
description: Bypass event logging exists asymmetrically across enforcement gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [enforcement, bypass-logging, observability-gap]
---

Push-gate bypass logging to `logs/hooks/review-gate-bypass.jsonl` is implemented in `scripts/enforcement/require-review-on-push.sh:149-167`, but commit-gate (`require-plan-approval.sh`) and runtime-gate (`.claude/hooks/plan-approval-gate.sh`) lack equivalent logging despite having bypass channels (`SKIP_PLAN_APPROVAL_GATE`, `SKIP_REVIEW_GATE`). This breaks end-to-end bypass observability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
