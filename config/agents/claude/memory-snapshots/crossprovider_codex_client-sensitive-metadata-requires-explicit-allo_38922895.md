---
name: crossprovider codex client-sensitive-metadata-requires-explicit-allo
description: Client-sensitive metadata requires explicit allowlist + governance rule, not just output filters
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [client-governance, metadata-allowlist, classification-mismatch]
---

Planned cleanup reports can mislabel client data (e.g., frontmatter says 'client: N/A' while index rows are marked 'sensitivity: client'). Output-side deny-lists do not catch this. Require an approved-root-label allowlist, define governance rules for each sensitivity class, and verify index row contents against plan assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
