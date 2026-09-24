---
name: crossprovider codex cleanup-audit-gates-both-temp-files-and-stale-li
description: Cleanup audit gates both temp files and stale links in touched content
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-audit, verification-gate, link-hygiene]
---

Audit scope includes accidental pdftotext.err/pdftoppm artifacts AND broken internal links already present in pages being augmented. Link validation prevents cascading broken targets; run link-probe on touched markdown before reporting completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
