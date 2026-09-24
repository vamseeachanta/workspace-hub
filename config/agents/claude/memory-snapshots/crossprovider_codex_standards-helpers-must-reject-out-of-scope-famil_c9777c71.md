---
name: crossprovider codex standards-helpers-must-reject-out-of-scope-famil
description: Standards helpers must reject out-of-scope families to avoid false standards provenance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, citations, api-design, scope-boundary]
---

When a standards-specific helper (e.g., DNV-RP-F106) accepts coating families not present in that standard's data sheets (e.g., POLYURETHANE) or silently coerces values (COAL_TAR_EPOXY → COAL_TAR_ENAMEL), and then emits citations for them, callers receive false traceability. Scope boundaries must be hard; reject or require explicit override for out-of-scope inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
