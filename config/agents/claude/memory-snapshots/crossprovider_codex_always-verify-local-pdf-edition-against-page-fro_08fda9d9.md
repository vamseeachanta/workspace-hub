---
name: crossprovider codex always-verify-local-pdf-edition-against-page-fro
description: Always verify local PDF edition against page frontmatter before ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [edition-accuracy, standards-sourcing]
---

Issue briefs and pages often claim editions unsupported by local PDFs (API Spec 4F local 2013 4th ed, page claims 2023 5th ed). Verify PDF metadata (title page, pdfinfo date) before writing or extending any page. "to be verified" revision entries signal never-confirmed facts; do not propagate them into new pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
