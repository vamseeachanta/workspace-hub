---
name: crossprovider codex infrastructure-operations-documentation-requires
description: Infrastructure/operations documentation requires security and legal validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [security, operations, documentation, process]
---

Operational docs with machine identifiers, addresses, or connection details must pass repository security scanners (`legal-sanity-scan.sh`, `secrets-scan.sh`) and link validation before merge to prevent leaking environment-specific information.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
