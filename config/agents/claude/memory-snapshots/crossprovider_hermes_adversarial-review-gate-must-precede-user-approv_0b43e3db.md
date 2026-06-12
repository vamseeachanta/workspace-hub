---
name: crossprovider hermes adversarial-review-gate-must-precede-user-approv
description: Adversarial review gate must precede user approval and merge
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-gate, code-review, approval-workflow]
---

Sessions show that independent adversarial review (Codex, Gemini, or cross-provider) is non-negotiable before presenting work for user approval or merge. Self-review during development is insufficient; the gate requires external, defect-hunting-focused review evidence before user consideration. Violations result in shipping undetected MAJOR defects.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
