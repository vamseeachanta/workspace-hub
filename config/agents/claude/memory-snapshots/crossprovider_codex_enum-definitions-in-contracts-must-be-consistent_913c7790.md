---
name: crossprovider codex enum-definitions-in-contracts-must-be-consistent
description: Enum definitions in contracts must be consistent across plan sections
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-clarity, plan-writing, correctness]
---

When a contract defines an enum or state set that appears in multiple plan sections (policy, implementation, acceptance criteria), verify all uses have identical meaning. Codex found auth_failed defined differently in policy versus operator-interface sections, creating a correctness-critical contradiction undetectable without cross-section comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
