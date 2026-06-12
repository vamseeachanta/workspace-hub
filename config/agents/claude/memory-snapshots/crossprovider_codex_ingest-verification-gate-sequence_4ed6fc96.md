---
name: crossprovider codex ingest-verification-gate-sequence
description: Ingest verification gate sequence
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, ingest, verification, qa]
---

Run gates in order before closure: (1) frontmatter/link probe, (2) conflict-marker check, (3) whitespace check (git diff --check), (4) legal scan (scripts/legal/legal-sanity-scan.sh or fallback grep). Redact licensee identifiers from generated CSVs before gates. All gates must PASS.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
