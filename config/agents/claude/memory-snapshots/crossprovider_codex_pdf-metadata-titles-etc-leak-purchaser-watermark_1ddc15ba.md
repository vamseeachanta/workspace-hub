---
name: crossprovider codex pdf-metadata-titles-etc-leak-purchaser-watermark
description: PDF metadata (titles, etc) leak purchaser/watermark info despite filename hashing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, metadata-leakage, repo-safety]
---

Filename hashing via `source_name_digest` does not cover PDF metadata titles copied verbatim into manifest rows (e.g., pdfinfo_title field). Purchaser names, watermark phrases, licensee strings remain exposed. Repo-safety check only blocks fixed substrings like `/mnt/`, not semantic private content. Either sanitize metadata or fail closed on private-content heuristics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
