---
name: crossprovider codex sanitize-generated-artifacts-from-local-source-p
description: Sanitize generated artifacts from local source paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [data-sanitization, security, code-generation, metadata]
---

Metadata pages may embed local file paths in frontmatter (e.g., `/home/user/source.pdf`). Generated JSON/HTML/wiki output must strip these; they leak environmental details and go stale across machines. Add explicit path sanitization during artifact render.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
