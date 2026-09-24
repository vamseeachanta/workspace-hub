---
name: crossprovider codex source-path-frontmatter-must-not-contaminate-gen
description: Source-path frontmatter must not contaminate generated output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [source-handling, data-sanitization]
---

Metadata resolver pages may carry local filesystem paths (e.g., `C:\source\...`) in YAML frontmatter. These must not be copied into generated JSON/HTML/wiki artifacts. Add sanitization tests that strip source paths from all generated output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
