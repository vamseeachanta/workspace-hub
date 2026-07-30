---
name: crossprovider codex allowed-root-validation-required-for-path-securi
description: Allowed-root validation required for path security
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [security, path-validation]
---

Path syntax checks alone (reject `..`, `/`, extensions) are insufficient; membership in allowed roots must be verified independently at security boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
