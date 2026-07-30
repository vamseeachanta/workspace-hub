---
name: crossprovider codex multi-party-transaction-economics-require-exhaus
description: Multi-party transaction economics require exhaustive scenario tests, not single golden case
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, economics, multi-party, acceptance-criteria]
---

Tests that check only one party's deterministic metrics (e.g., Talos final net cash) miss consideration-separation bugs across multiple buyers/scenarios. Each distinct party, scenario, or commercial branch (Shell, Talos, Ridgewood, BP-exercise, etc.) must have explicit numeric test cases with expected values, not just section-presence checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
