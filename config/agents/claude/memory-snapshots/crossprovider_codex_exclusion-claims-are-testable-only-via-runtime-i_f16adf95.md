---
name: crossprovider codex exclusion-claims-are-testable-only-via-runtime-i
description: Exclusion claims are testable only via runtime instrumentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, privacy, instrumentation]
---

'We don't access X at runtime' is only verifiable through RED tests confirming the runtime never opens, imports, or calls X. Code inspection or prose claims are insufficient; instrument the runtime to verify exclusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
