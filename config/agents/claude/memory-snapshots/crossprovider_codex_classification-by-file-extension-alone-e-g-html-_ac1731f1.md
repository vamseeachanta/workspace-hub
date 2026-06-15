---
name: crossprovider codex classification-by-file-extension-alone-e-g-html-
description: Classification by file extension alone (e.g., HTML) is too permissive
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, classification, heuristic-gaps]
---

Maritime regulatory manifest promotes HTML files to source-candidates solely by extension, so archive/bundle HTML and unrelated private HTML (e.g., receipt pages) become candidates. Require domain-specific, semantic classification: HTML must pass per-publisher rules and content inspection, not just extension matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
