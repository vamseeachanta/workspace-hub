---
name: crossprovider codex accidental-pdf-tool-artifacts-during-read-only-e
description: Accidental PDF-tool artifacts during read-only exploration
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [read-only-safety, scratch-artifacts, pdf-tools]
---

PDF exploration tooling (`pdftotext`, `pdfimages`, OCR passes) can silently create scratch files (-.png, -.pgm, -.tmp) in the worktree even in read-only inspection sessions. Clean them up immediately and verify `git status --short` is clean afterward. Use `2>/dev/null` redirects or temp paths to prevent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
