---
name: crossprovider codex sparse-checkout-omissions-break-validation-test-
description: Sparse-checkout omissions break validation test runs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sparse-checkout, test-failures, path-discovery]
---

Approved validation tests fail when sparse-checkout omits referenced paths (fixtures, schema docs, config files). Incrementally expand sparse-checkout for each missing path: `git sparse-checkout add <path>`. Each validation run may surface new sparse gaps; re-run after expansion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
