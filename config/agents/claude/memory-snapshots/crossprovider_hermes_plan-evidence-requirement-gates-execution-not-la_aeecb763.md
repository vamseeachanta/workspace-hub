---
name: crossprovider hermes plan-evidence-requirement-gates-execution-not-la
description: Plan evidence requirement gates execution, not labels alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval, gates, hygiene, github-workflow]
---

Do not launch implementation from `status:plan-approved` labels. Require: (1) live `.planning/plan-approved/<issue>.md` approval marker, (2) clean repo/worktree state, (3) no `status:working` label. Label drift and missing approval evidence are repair-only work, not executable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
