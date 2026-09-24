---
name: crossprovider gemini identity-contract-dual-model-sha256-primary-md5-
description: Identity contract dual-model: sha256 primary + md5 legacy read-only
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [standards, data-governance, backward-compatibility]
---

Forward-compatible identity scheme: sha256:<64-hex> is primary (identity_status: ok); md5:<hex> permitted for legacy-data reads with status annotation (identity_status: legacy-read-only). This resolves tension between enforcing new standard and supporting existing data without forcing migration; same rule applied at both CLI and conformance-check stages to prevent contradiction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
