---
name: crossprovider codex plan-authorization-gates-need-external-event-bin
description: Plan authorization gates need external event binding, not text markers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [authorization, plan-safety, validation, provenance]
---

A gate checking only for `Approval source:` text line is satisfied by locally authored markers. True authorization requires tying the approval marker to an external GitHub event ID, webhook payload timestamp, or signed identity—not just the presence of a string. Plans claiming "externally approved" without provenance validation will pass false positives and bypass intended reviews.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
