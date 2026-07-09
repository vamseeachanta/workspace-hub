---
name: crossprovider codex hard-coded-issue-plan-numbers-in-config-block-sc
description: Hard-coded issue/plan numbers in config block scope generalization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [config-design, scope-generalization, magic-strings]
---

Allow-context path validation was hard-coded to accept only `issue-68` and `plan-68` sentinel values in `scripts/ace_public_surface_rules.py` and `config/ace-public-surface-self-scan-contract.json`. When a follow-on issue #72 tried to generalize the pattern to new issues, the old magic strings became a blocker. Parameterized path logic or explicit scope boundaries are needed when config couples to specific issue numbers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
