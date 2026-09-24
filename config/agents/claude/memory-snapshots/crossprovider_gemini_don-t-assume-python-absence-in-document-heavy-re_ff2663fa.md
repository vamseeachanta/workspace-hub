---
name: crossprovider gemini don-t-assume-python-absence-in-document-heavy-re
description: Don't assume Python absence in document-heavy repos; verify usage
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [codebase-assessment, scope-discovery, documentation]
---

Content-heavy repos may have tracked but entirely unused Python scaffolding. Verify actual traffic and file counts before deciding scope (e.g., 495 markdown vs 12 Python files, zero Python CI traffic = docs-only despite Python presence).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
