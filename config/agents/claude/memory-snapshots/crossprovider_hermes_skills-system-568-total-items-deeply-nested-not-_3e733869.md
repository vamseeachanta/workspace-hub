---
name: crossprovider hermes skills-system-568-total-items-deeply-nested-not-
description: Skills system: 568 total items deeply nested, not flat
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills-system, directory-structure, codebase-organization]
---

The .claude/skills/ directory contains 568 SKILL.md files across 12 categories (_core 53, _internal 128, ai 9, business 70, data 77, development 52, digitalmodel 2, engineering 87, gsd-* 57, operations 15, science 6, workspace-hub 12). Skills use deep nesting (e.g., _core/bash/bash-cli-framework/1-always-use-set-e/SKILL.md) rather than flat lists. Skill discovery and indexing tools need to traverse the tree recursively.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
