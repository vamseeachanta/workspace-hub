---
name: crossprovider codex security-enforcement-test-for-self-inflicted-byp
description: Security enforcement: test for self-inflicted bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [security, testing, edge-cases, adversarial]
---

Adversarial testing of security scanners must include cases where the tool's own code (regex variable names, literal strings in enforcement logic) would trigger its own rules. Self-safety validation catches false negatives that bypass tests miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
