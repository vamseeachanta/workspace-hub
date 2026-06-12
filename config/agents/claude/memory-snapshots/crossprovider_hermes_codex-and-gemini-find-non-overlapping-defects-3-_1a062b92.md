---
name: crossprovider hermes codex-and-gemini-find-non-overlapping-defects-3-
description: Codex and Gemini find non-overlapping defects; 3+ rounds indicate divergence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, adversarial-review, multi-provider, defect-hunting]
---

Multi-provider adversarial review: Codex finds defects Claude misses, Gemini finds others. If 3+ rounds show MAJOR severity and no convergence, surface the consensus-vs-minority findings instead of auto-cycling. Stale reviews (pre-patch) become invalid after code fixes; re-run after patches for fresh defect context.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
