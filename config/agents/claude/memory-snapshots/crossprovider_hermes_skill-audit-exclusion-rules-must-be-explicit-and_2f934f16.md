---
name: crossprovider hermes skill-audit-exclusion-rules-must-be-explicit-and
description: Skill audit exclusion rules must be explicit and enumerated
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, rules, filtering, specification]
---

Exclusion of paths like `_archive`, `_diverged`, `_core`, `_internal` needs explicit rules (what to exclude entirely vs. what to mark informational-only). Cannot rely on intuition; rules must be documented and covered by tests to avoid surprising noise in later audit runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
