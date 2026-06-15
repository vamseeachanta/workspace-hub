---
name: crossprovider codex metadata-values-must-align-with-descriptions-res
description: Metadata values must align with descriptions; resolve trust-label conflicts before merge
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [metadata-consistency, vocabulary-correctness, merge-safety]
---

Frontmatter metadata (e.g., trust_label: verified, derivation_status: quoted) must match the actual description. Don't mark something 'verified/quoted' if the description says 'standard assumption' or 'unverified input.' Audit every metadata assignment to ensure consistency before merging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
