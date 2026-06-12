---
name: crossprovider hermes registry-schema-can-be-incompatible-with-policy-
description: Registry schema can be incompatible with policy validators on live artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, live-artifacts, policy-loader]
---

Live registries may intentionally omit optional fields (e.g., `storage` for not-onboarded hosts), but policy loaders can hard-require them, causing validators to fail. Regression tests must run against real checked-in registry, not just synthetic fixtures. Fixes: either relax validation for disabled/not-onboarded hosts, or ensure schema is consistent.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
