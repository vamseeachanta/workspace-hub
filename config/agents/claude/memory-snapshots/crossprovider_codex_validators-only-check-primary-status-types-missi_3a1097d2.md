---
name: crossprovider codex validators-only-check-primary-status-types-missi
description: Validators only check primary status types, missing contradictory invariants in secondary paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, validator-design, invariant-enforcement]
---

Issue #290 shows validators enforcing row_count/cap_policy only for status=quarantined, not status=exported, allowing exported rows with contradictory completeness_class. Fix: when adding a new status type or field, explicitly audit which validators apply and add tests for all affected code paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
