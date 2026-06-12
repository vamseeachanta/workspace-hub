---
name: crossprovider hermes readonly-behavior-tests-fail-green-when-testing-
description: Readonly behavior tests fail green when testing unit functions instead of full CLI paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-gaps, false-green, test-coverage]
---

A test labeled `test_checker_is_readonly` exercised only the `check_machine()` function but missed the `--output` file-write behavior in the CLI main path. This allowed a readonly violation to ship. Readonly tests must exercise the complete runtime entry point (CLI args, actual output paths), not just unit functions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
