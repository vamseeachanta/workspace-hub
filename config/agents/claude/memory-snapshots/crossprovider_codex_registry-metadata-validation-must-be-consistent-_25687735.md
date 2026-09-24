---
name: crossprovider codex registry-metadata-validation-must-be-consistent-
description: Registry metadata validation must be consistent across all consumer paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata-contracts, validation-consistency, data-integrity]
---

A data registry can pass initial conversion validation but fail sidecar writing or report ingestion if metadata fields (e.g., version, date, source hash) are validated inconsistently. Each consumer (loader, writer, reader) must have the same strict requirements or silent data loss occurs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
