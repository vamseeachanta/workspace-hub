---
name: crossprovider codex pdf-tool-temp-file-artifacts-stream-or-isolate
description: PDF tool temp file artifacts: stream or isolate
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-tools, temp-artifacts, pdftotext, pdftoppm, cleanup]
---

pdftotext stderr redirection and pdftoppm `-` prefix create unintended files in cwd (/tmp/pdftotext.err, -.png). Stream to stdout or use explicit /tmp isolation with cleanup. Check git status after inspection runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
