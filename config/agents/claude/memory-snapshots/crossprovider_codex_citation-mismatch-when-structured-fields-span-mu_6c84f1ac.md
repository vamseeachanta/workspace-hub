---
name: crossprovider codex citation-mismatch-when-structured-fields-span-mu
description: Citation mismatch when structured fields span multiple sources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, source-policy, registry-design]
---

When a factor (e.g., API gravity) is accepted from one source but the same record has additional structured fields (min/max API, density) from a different source, the citation metadata must either support multi-source tracking or remove the unsupported fields to a caveat/evidence_note. Prevents downstream readers interpreting all fields as sourced from the primary citation URL.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
