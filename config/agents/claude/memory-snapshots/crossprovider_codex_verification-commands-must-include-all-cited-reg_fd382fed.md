---
name: crossprovider codex verification-commands-must-include-all-cited-reg
description: Verification commands must include all cited regression tests to avoid coverage gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [test-regression, command-completeness, gate-parity]
---

Plan cited `test_repo_supplemental_folder_inventory.py` as a regression guard but the verification command did not include it. Omitting named tests breaks the regression gate; every cited test must appear in the verification command exactly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
