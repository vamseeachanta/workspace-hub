---
name: crossprovider codex existing-page-content-defeats-broad-absence-test
description: Existing page content defeats broad absence tests; use pre/post inventory instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-design, file-modification, diff-safety]
---

When modifying tracked files, broad test rules like "pages must not contain X" fail on existing content. Use `git diff` pre/post inventory or section-boundary scanning instead. Mark generated sections with start/end boundaries so tests isolate new content from existing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
