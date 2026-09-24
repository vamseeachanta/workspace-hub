---
name: crossprovider codex raw-traversal-verification-complements-high-leve
description: Raw traversal verification complements high-level library walks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, audit, completeness]
---

Library-level walks (python-pptx, pandas, lxml) can miss content that raw file/zip traversal finds (e.g., XML fallback content, orphaned parts, alternate content). For audit and inventory work, cross-check with raw package/file traversal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
