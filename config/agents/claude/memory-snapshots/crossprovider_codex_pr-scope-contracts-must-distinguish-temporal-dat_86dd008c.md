---
name: crossprovider codex pr-scope-contracts-must-distinguish-temporal-dat
description: PR scope contracts must distinguish temporal data from derived scalars
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope, testing, data-modeling, contract-enforcement]
---

When a PR explicitly excludes intensity measures, publishing derived peak values (PGV, PGD) in summaries/reports violates the contract even if temporal time-series are in scope. Handle time-domain and frequency-domain outputs in separate slices aligned to PR boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
