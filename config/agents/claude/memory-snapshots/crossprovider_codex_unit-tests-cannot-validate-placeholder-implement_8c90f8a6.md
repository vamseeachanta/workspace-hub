---
name: crossprovider codex unit-tests-cannot-validate-placeholder-implement
description: Unit tests cannot validate placeholder implementations against real acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, test-design]
---

Tests that pass synthetic fixtures can bless placeholder implementations (caption inventories instead of tables, summaries instead of full extraction). Verification must compare generated real-source output against explicit approved-plan acceptance criteria to catch scope gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
