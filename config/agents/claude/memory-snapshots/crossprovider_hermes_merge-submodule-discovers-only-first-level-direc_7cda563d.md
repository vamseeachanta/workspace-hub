---
name: crossprovider hermes merge-submodule-discovers-only-first-level-direc
description: merge-submodule discovers only first-level directories, missing nested skills
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills-discovery, nested-scope-gap, design-limitation]
---

The merge-submodule skill discovery script enumerates only first-level `.claude/skills/` directories, missing nested skills like `digitalmodel/converted-agents/engineering/`. This breaks discovery for nested repos and prevents comprehensive skill propagation. Recursive walk needed to satisfy skill ecosystem acceptance criteria.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
