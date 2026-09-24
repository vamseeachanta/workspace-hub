---
name: crossprovider codex raw-source-pdfs-stay-off-repo-only-derived-data-
description: Raw source PDFs stay off-repo; only derived data and metadata commit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, git, licensing, pdf-handling]
---

Source PDFs are referenced by file path only (e.g., `source_pdf: /mnt/ace/O&G-Standards/ISO/...pdf`). Extracted tables, figures, and frontmatter metadata live in the repo; the raw PDF never commits. This separation keeps licensing and data handling clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
