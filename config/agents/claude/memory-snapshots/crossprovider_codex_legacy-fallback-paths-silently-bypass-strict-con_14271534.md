---
name: crossprovider codex legacy-fallback-paths-silently-bypass-strict-con
description: Legacy fallback paths silently bypass strict contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-breach, legacy-compatibility, production-risk]
---

Embedded test fixtures with hardcoded conversion values (e.g., 7.33 bbl/tonne) can serve production data without triggering new validation layers or audit requirements, even when strict contracts have been defined elsewhere in the codebase. Production-mode adapters may still use committed fallback data that pre-dates the new audit/provenance contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
