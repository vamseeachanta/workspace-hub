---
name: crossprovider codex ingest-dependencies-install-to-tmp-as-disposable
description: Ingest dependencies install to /tmp as disposable; do not modify worktree
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, dependencies, tooling, environment]
---

If pdfplumber, tesseract, or other extraction tools are not pre-installed in the worktree Python, install them into /tmp as a disposable environment. This keeps the repo clean and avoids coupling ingest pipelines to the worktree's package state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
