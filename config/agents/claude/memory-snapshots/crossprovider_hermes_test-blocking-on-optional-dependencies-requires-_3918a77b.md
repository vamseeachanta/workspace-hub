---
name: crossprovider hermes test-blocking-on-optional-dependencies-requires-
description: Test blocking on optional dependencies requires clear docs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, dependencies, environment-setup]
---

When tests require conditional dependencies (e.g., assetutilities for hydrodynamics tests), blocking on missing env is expected, but error messages must be clear and workaround documented (use CI/full-test suite, or manual install). Don't silently skip; surface it as 'env incomplete'.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
