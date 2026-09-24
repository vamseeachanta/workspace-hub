---
name: crossprovider codex tdd-sections-can-look-complete-while-only-testin
description: TDD sections can look complete while only testing governance, not code work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd-validation, test-coverage, work-alignment]
---

Issue #2452 TDD rows were all process checks (`test_inventory_groups_top_rule_families`, `test_child_issue_split_is_recorded`) while the parent issue required source-tree flake8 remediation. No failing tests specified for actual cleanup waves or rule families (E722, F841, etc.). Adversarial reviews should verify TDD directly exercises the work being planned, not just documents its existence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
