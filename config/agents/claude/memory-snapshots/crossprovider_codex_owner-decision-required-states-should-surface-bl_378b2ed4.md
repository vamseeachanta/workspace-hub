---
name: crossprovider codex owner-decision-required-states-should-surface-bl
description: Owner-decision-required states should surface blockers, not be fabricated
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, decision-making, testing-integrity]
---

When evidence legitimately yields no decisive winner (missing proof, equally valid candidates, or blocked primary requirements), emit `owner_decision_required` rather than inventing a choice or using a fallback. Auditable neutrality and deferred human decision are preferable to hidden fabrication. Tests must not hardcode expected winners when evidence does not justify them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
