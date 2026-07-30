---
name: crossprovider codex cited-source-files-in-plan-not-verified-by-revie
description: Cited source files in plan not verified by reviewers — deferred evidence checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [codex, adversarial-review, evidence, file-verification]
---

Plan's "Resource Intelligence Summary" cites `artifacts/ace-wave0-ledger-schema.json`, `scripts/validate_ace_wave0_schema_contract.py`, etc. as authoritative sources, but reviewers' Retrieval sections never confirm these files exist or contain the claimed contracts. Adding explicit file-existence verification to the adversarial-review prompt ("Verify each cited source file exists and cite its path") will surface missing dependencies earlier.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
