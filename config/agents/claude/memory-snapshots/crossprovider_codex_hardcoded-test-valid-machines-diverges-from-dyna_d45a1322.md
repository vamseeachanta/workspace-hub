---
name: crossprovider codex hardcoded-test-valid-machines-diverges-from-dyna
description: Hardcoded test VALID_MACHINES diverges from dynamic registry
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, registry, test-maintenance]
---

validate-schedule.py loads valid machine names from registry.yaml at runtime, but test_validate_schedule.py hardcodes VALID_MACHINES. When a new machine is added to the registry, live validation passes but tests fail, causing inconsistent coverage and skipped test runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
