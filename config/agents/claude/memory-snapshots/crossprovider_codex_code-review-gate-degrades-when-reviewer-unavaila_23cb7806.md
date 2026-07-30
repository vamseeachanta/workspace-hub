---
name: crossprovider codex code-review-gate-degrades-when-reviewer-unavaila
description: Code review gate degrades when reviewer unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [code-review, governance, gates, policy]
---

When a required code reviewer becomes unavailable (e.g., due to authentication requirements), the gate degrades per policy (e.g., T3→T2 in this repo) rather than proceeding without review or substituting an unverified verdict; document the degradation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
