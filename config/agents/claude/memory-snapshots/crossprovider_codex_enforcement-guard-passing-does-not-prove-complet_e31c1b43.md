---
name: crossprovider codex enforcement-guard-passing-does-not-prove-complet
description: Enforcement guard passing does not prove complete correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, testing-gaps, adversarial-review]
---

A guard command passing means indexed files meet that specific constraint. It does not catch schema blind spots, unexercised codepaths, governance gaps, or transitive surfaces. Adversarial reviews must hunt for paths and assumptions the guard does not exercise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
