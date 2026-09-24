---
name: crossprovider codex resolver-fail-open-hazard-existence-check-before
description: Resolver fail-open hazard: existence-check before policy constraints
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-pattern, resolver-hazard, fail-open]
---

When a resolver has multiple fallback paths, applying existence-checks before policy constraints (like source-root limits) enables fail-open behavior. A path outside constraints can be accepted if it exists on the filesystem. Constraints must come first in the fallback chain.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
