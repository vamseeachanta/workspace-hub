---
name: crossprovider codex scheduler-mutation-tests-need-adversarial-covera
description: Scheduler mutation tests need adversarial coverage for ordering and sentinels
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [testing, security]
---

Unit tests must separately cover branch-mechanism derivation, transaction-step reordering, guard-before-exec timing, sentinel parsing, and disposition binding. These ordering and parsing bugs don't surface in integration tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
