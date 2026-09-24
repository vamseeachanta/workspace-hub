---
name: crossprovider codex caller-supplied-parameters-bypass-validation-if-
description: Caller-supplied parameters bypass validation if invariants are enforced at the wrong layer
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, api-design, invariant-enforcement]
---

When an API accepts caller-supplied configuration (e.g., catalog, config objects), validation constraints defined elsewhere (e.g., in the data-source loader) do not automatically apply. A refresh API that accepts an injected catalog without re-validating official-host constraints allows attackers to pass custom download URLs that defeat the intended invariant. Enforce critical boundaries (official sources, deny-lists, access controls) at the API entry point, not just at the initial data loader.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
