---
name: crossprovider hermes multi-provider-adversarial-reviews-require-full-
description: Multi-provider adversarial reviews require full provenance record: verdict + artifact + commit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, multi-provider, provenance]
---

Plans require review from non-authoring providers (Codex T1, Claude T2, Gemini). Each verdict must record: verdict level (APPROVE/MINOR/MAJOR), artifact path, issue/PR comment URL, exact revision/commit SHA evaluated. Deferred reviews (e.g., 'Claude T2 scheduled for morning') must be explicitly marked; missing verdict artifact indicates incomplete review, not approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
