---
name: crossprovider codex pause-resume-criteria-for-public-infrastructure-
description: Pause/resume criteria for public infrastructure must be precise and auditable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, compliance-gate, automation-safety]
---

When a cron job is paused for legal/ToS reasons, soft resume gates ('when we feel ready') create compliance risk. Define a U1-U5 style auditable checklist (U1: cease-and-desist runbook committed, U2: TOS_REVIEW.md signed, etc.) that can be checked mechanically or documented explicitly. 'Urgency framing' is not a gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
